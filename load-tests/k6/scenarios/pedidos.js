// Teste de carga do fluxo de criação de pedido (POST /orders/).
//
// Cada requisição aciona o fluxo completo: usuário → estoque → pagamento → persistência.
// O cenário é escolhido via variável de ambiente:
//
//   CENARIO      baixa (10 req/s) | moderada (100 req/s) | alta (500 req/s) | rampup (10 → 500 req/s)
//   AQUECIMENTO  segundos de aquecimento antes da medição (default 30; não entram nos resultados)
//   MEDICAO      segundos de medição (default 60)
//   SAIDA        diretório onde gravar k6_resumo.json e k6_completo.json (opcional)
//   BASE_URL     URL do serviço de pedidos (default http://localhost:8000)
//
// Exemplo: k6 run -e CENARIO=moderada scenarios/pedidos.js

import http from 'k6/http';
import { check } from 'k6';
import { Counter, Rate } from 'k6/metrics';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const CENARIO = __ENV.CENARIO || 'baixa';
const AQUECIMENTO = parseInt(__ENV.AQUECIMENTO || '30', 10);
const MEDICAO = parseInt(__ENV.MEDICAO || '60', 10);
const SAIDA = __ENV.SAIDA || '';

const TAXAS = { baixa: 10, moderada: 100, alta: 500 };
const RAMPUP = { inicial: 10, alvos: [100, 250, 500, 500] }; // 4 estágios de MEDICAO/4 cada

if (CENARIO !== 'rampup' && !(CENARIO in TAXAS)) {
  throw new Error(`CENARIO inválido: ${CENARIO}. Use baixa, moderada, alta ou rampup.`);
}

// Payload fixo em todas as execuções (variável de controle).
const PAYLOAD = JSON.stringify({
  user_id: 'user-1',
  items: [{ product_id: 'mouse', quantity: 1, unit_price: '50.00' }],
});
const TIMEOUT_MS = 10000;
const PARAMS = { headers: { 'Content-Type': 'application/json' }, timeout: `${TIMEOUT_MS}ms` };

// Separa os dois tipos de "erro" do fluxo:
// - recusa de pagamento (402) é resultado de negócio esperado (decline_rate de 5%)
// - erro técnico é qualquer outra falha (5xx, timeout, conexão recusada...)
const recusas = new Rate('pedidos_recusados');
const errosTecnicos = new Rate('erros_tecnicos');

// Durações acima do timeout são fisicamente impossíveis: indicam salto no relógio do host
// (observado no WSL2). A execução afetada deve ser descartada ou ter a média desconsiderada.
const amostrasSuspeitas = new Counter('amostras_suspeitas');

function dimensionarVUs(taxaMax) {
  // VUs necessários ≈ taxa × latência. Com o teto em 2× a taxa, o k6 sustenta até ~2 s de
  // latência; acima disso descarta iterações (registradas em dropped_iterations).
  return { preAllocatedVUs: Math.max(10, taxaMax), maxVUs: Math.min(Math.max(50, taxaMax * 2), 1000) };
}

function cenarioMedicao() {
  if (CENARIO === 'rampup') {
    return {
      executor: 'ramping-arrival-rate',
      startRate: RAMPUP.inicial,
      timeUnit: '1s',
      stages: RAMPUP.alvos.map((target) => ({ target, duration: `${MEDICAO / 4}s` })),
      ...dimensionarVUs(Math.max(...RAMPUP.alvos)),
    };
  }
  return {
    executor: 'constant-arrival-rate',
    rate: TAXAS[CENARIO],
    timeUnit: '1s',
    duration: `${MEDICAO}s`,
    ...dimensionarVUs(TAXAS[CENARIO]),
  };
}

const scenarios = {
  medicao: { ...cenarioMedicao(), startTime: `${AQUECIMENTO}s`, gracefulStop: '10s' },
};
if (AQUECIMENTO > 0) {
  const taxa = CENARIO === 'rampup' ? RAMPUP.inicial : TAXAS[CENARIO];
  scenarios.aquecimento = {
    executor: 'constant-arrival-rate',
    rate: taxa,
    timeUnit: '1s',
    duration: `${AQUECIMENTO}s`,
    ...dimensionarVUs(taxa),
    gracefulStop: '5s',
  };
}

// Os thresholds abaixo sempre passam: servem para o k6 calcular as submétricas filtradas
// pelo cenário "medicao", excluindo o aquecimento do resumo.
const SO_MEDICAO = '{scenario:medicao}';
export const options = {
  scenarios,
  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(90)', 'p(95)', 'p(99)'],
  thresholds: {
    [`http_req_duration${SO_MEDICAO}`]: ['max>=0'],
    [`http_req_failed${SO_MEDICAO}`]: ['rate>=0'],
    [`http_reqs${SO_MEDICAO}`]: ['count>=0'],
    [`pedidos_recusados${SO_MEDICAO}`]: ['rate>=0'],
    [`erros_tecnicos${SO_MEDICAO}`]: ['rate>=0'],
    [`dropped_iterations${SO_MEDICAO}`]: ['count>=0'],
    [`amostras_suspeitas${SO_MEDICAO}`]: ['count>=0'],
  },
};

export default function () {
  const res = http.post(`${BASE_URL}/orders/`, PAYLOAD, PARAMS);
  recusas.add(res.status === 402);
  errosTecnicos.add(res.status !== 201 && res.status !== 402);
  if (res.timings.duration > TIMEOUT_MS) amostrasSuspeitas.add(1);
  check(res, { 'pedido criado ou recusado': (r) => r.status === 201 || r.status === 402 });
}

function valores(data, metrica) {
  const m = data.metrics[`${metrica}${SO_MEDICAO}`];
  return m ? m.values : {};
}

function arredondar(v, casas = 3) {
  return v === undefined || v === null ? null : Number(v.toFixed(casas));
}

export function handleSummary(data) {
  const dur = valores(data, 'http_req_duration');
  const requisicoes = valores(data, 'http_reqs').count || 0;

  const resumo = {
    cenario: CENARIO,
    taxa_alvo_rps: CENARIO === 'rampup' ? `${RAMPUP.inicial}->${Math.max(...RAMPUP.alvos)}` : TAXAS[CENARIO],
    aquecimento_s: AQUECIMENTO,
    medicao_s: MEDICAO,
    requisicoes,
    throughput_rps: arredondar(requisicoes / MEDICAO, 4),
    latencia_media_ms: arredondar(dur.avg),
    latencia_mediana_ms: arredondar(dur.med),
    latencia_p90_ms: arredondar(dur['p(90)']),
    latencia_p95_ms: arredondar(dur['p(95)']),
    latencia_p99_ms: arredondar(dur['p(99)']),
    latencia_min_ms: arredondar(dur.min),
    latencia_max_ms: arredondar(dur.max),
    taxa_erro_pct: arredondar((valores(data, 'http_req_failed').rate || 0) * 100, 4),
    taxa_recusa_pct: arredondar((valores(data, 'pedidos_recusados').rate || 0) * 100, 4),
    taxa_erro_tecnico_pct: arredondar((valores(data, 'erros_tecnicos').rate || 0) * 100, 4),
    iteracoes_descartadas: valores(data, 'dropped_iterations').count || 0,
    amostras_suspeitas: valores(data, 'amostras_suspeitas').count || 0,
  };

  const saida = { stdout: JSON.stringify(resumo, null, 2) + '\n' };
  if (SAIDA) {
    saida[`${SAIDA}/k6_resumo.json`] = JSON.stringify(resumo, null, 2);
    saida[`${SAIDA}/k6_completo.json`] = JSON.stringify(data, null, 2);
  }
  return saida;
}
