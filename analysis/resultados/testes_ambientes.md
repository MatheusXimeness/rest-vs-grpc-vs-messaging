## Comparação entre ambientes (local × nuvem)

| Cenário | Estratégia | Métrica | Mediana local × nuvem | p (posição) | δ nuvem vs local | CV local × nuvem (%) | p (variância) |
|---|---|---|---|---|---|---|---|
| baixa | REST | Latência média (ms) | 19,90 × 16,65 | < 0,001 | -1,00 (grande) | 5,2 × 6,6 | 0,384 |
| baixa | REST | Latência mediana (ms) | 19,38 × 16,39 | < 0,001 | -1,00 (grande) | 3,3 × 7,1 | 0,911 |
| baixa | REST | Latência p95 (ms) | 23,75 × 18,20 | < 0,001 | -1,00 (grande) | 12,2 × 4,5 | 0,064 |
| baixa | REST | Throughput (req/s) | 10,01 × 10,00 | 0,693 | -0,10 (desprezível) | 0,1 × 0,1 | 0,548 |
| baixa | REST | Erro técnico (%) | 0,00 × 0,00 | 1,000 | 0,00 (desprezível) | — × — | — |
| baixa | REST | CPU total (% de 1 núcleo) | 19,2 × 16,7 | < 0,001 | -1,00 (grande) | 3,9 × 7,6 | 0,982 |
| baixa | REST | Memória total (MB) | 385,0 × 353,6 | < 0,001 | -1,00 (grande) | 0,5 × 0,3 | 0,243 |
| baixa | gRPC | Latência média (ms) | 16,77 × 13,95 | < 0,001 | -1,00 (grande) | 8,6 × 0,6 | 0,037 |
| baixa | gRPC | Latência mediana (ms) | 16,34 × 13,82 | < 0,001 | -1,00 (grande) | 2,7 × 0,6 | 0,022 |
| baixa | gRPC | Latência p95 (ms) | 20,99 × 15,20 | < 0,001 | -1,00 (grande) | 17,1 × 0,7 | 0,021 |
| baixa | gRPC | Throughput (req/s) | 10,02 × 10,02 | 0,144 | 0,30 (pequeno) | 0,1 × 0,1 | 0,135 |
| baixa | gRPC | Erro técnico (%) | 0,00 × 0,00 | 1,000 | 0,00 (desprezível) | — × — | — |
| baixa | gRPC | CPU total (% de 1 núcleo) | 16,1 × 14,1 | < 0,001 | -1,00 (grande) | 5,6 × 1,0 | 0,067 |
| baixa | gRPC | Memória total (MB) | 405,1 × 372,3 | < 0,001 | -1,00 (grande) | 1,2 × 0,2 | 0,016 |
| baixa | Mensageria | Latência média (ms) | 20,71 × 16,51 | < 0,001 | -1,00 (grande) | 16,5 × 3,5 | 0,116 |
| baixa | Mensageria | Latência mediana (ms) | 19,22 × 15,73 | < 0,001 | -1,00 (grande) | 7,6 × 1,3 | 0,031 |
| baixa | Mensageria | Latência p95 (ms) | 31,46 × 20,56 | 0,003 | -0,80 (grande) | 30,6 × 20,5 | 0,233 |
| baixa | Mensageria | Throughput (req/s) | 10,02 × 10,01 | 0,185 | -0,30 (pequeno) | 0,1 × 0,1 | 0,037 |
| baixa | Mensageria | Erro técnico (%) | 0,00 × 0,00 | 1,000 | 0,00 (desprezível) | — × — | — |
| baixa | Mensageria | CPU total (% de 1 núcleo) | 34,1 × 29,8 | 0,009 | -0,70 (grande) | 12,4 × 3,0 | 0,063 |
| baixa | Mensageria | Memória total (MB) | 531,6 × 499,2 | < 0,001 | -1,00 (grande) | 1,5 × 0,3 | 0,076 |
| moderada | REST | Latência média (ms) | 879,81 × 16,75 | 0,003 | -0,80 (grande) | 78,5 × 154,3 | 0,008 |
| moderada | REST | Latência mediana (ms) | 854,41 × 16,30 | 0,001 | -0,88 (grande) | 85,9 × 245,9 | 0,004 |
| moderada | REST | Latência p95 (ms) | 1.630,96 × 19,16 | 0,002 | -0,82 (grande) | 80,4 × 152,2 | 0,071 |
| moderada | REST | Throughput (req/s) | 98,82 × 100,01 | 0,018 | 0,62 (grande) | 2,7 × 0,2 | 0,062 |
| moderada | REST | Erro técnico (%) | 0,00 × 0,00 | 0,585 | -0,12 (desprezível) | 278,1 × 225,0 | 0,353 |
| moderada | REST | CPU total (% de 1 núcleo) | 339,0 × 136,3 | 0,003 | -0,80 (grande) | 32,5 × 31,5 | 0,098 |
| moderada | REST | Memória total (MB) | 476,6 × 408,9 | < 0,001 | -0,96 (grande) | 4,5 × 2,9 | 0,166 |
| moderada | gRPC | Latência média (ms) | 30,98 × 14,53 | < 0,001 | -1,00 (grande) | 230,6 × 1,2 | 0,250 |
| moderada | gRPC | Latência mediana (ms) | 17,42 × 14,49 | < 0,001 | -1,00 (grande) | 271,3 × 0,9 | 0,327 |
| moderada | gRPC | Latência p95 (ms) | 47,34 × 16,18 | < 0,001 | -1,00 (grande) | 187,5 × 1,1 | 0,133 |
| moderada | gRPC | Throughput (req/s) | 100,02 × 100,02 | 0,078 | 0,30 (pequeno) | 1,3 × 0,0 | 0,326 |
| moderada | gRPC | Erro técnico (%) | 0,00 × 0,00 | 1,000 | 0,00 (desprezível) | — × — | — |
| moderada | gRPC | CPU total (% de 1 núcleo) | 146,2 × 107,9 | < 0,001 | -1,00 (grande) | 32,6 × 1,5 | 0,213 |
| moderada | gRPC | Memória total (MB) | 444,0 × 411,1 | < 0,001 | -1,00 (grande) | 3,2 × 0,4 | 0,253 |
| moderada | Mensageria | Latência média (ms) | 521,86 × 17,86 | < 0,001 | -1,00 (grande) | 82,9 × 3,4 | 0,005 |
| moderada | Mensageria | Latência mediana (ms) | 316,88 × 15,52 | < 0,001 | -1,00 (grande) | 98,8 × 1,1 | 0,010 |
| moderada | Mensageria | Latência p95 (ms) | 1.608,40 × 35,56 | < 0,001 | -1,00 (grande) | 58,4 × 7,6 | < 0,001 |
| moderada | Mensageria | Throughput (req/s) | 98,74 × 100,00 | < 0,001 | 0,94 (grande) | 6,6 × 0,0 | 0,021 |
| moderada | Mensageria | Erro técnico (%) | 0,00 × 0,00 | 1,000 | 0,00 (desprezível) | — × — | — |
| moderada | Mensageria | CPU total (% de 1 núcleo) | 275,9 × 144,1 | < 0,001 | -1,00 (grande) | 15,7 × 1,2 | 0,002 |
| moderada | Mensageria | Memória total (MB) | 584,4 × 541,8 | < 0,001 | -1,00 (grande) | 2,2 × 0,2 | 0,016 |
| alta | REST | Latência média (ms) | 10.287,91 × 8.401,96 | < 0,001 | -1,00 (grande) | 1,4 × 3,7 | 0,625 |
| alta | REST | Latência mediana (ms) | 10.000,57 × 8.168,91 | < 0,001 | -1,00 (grande) | 0,0 × 3,9 | 0,056 |
| alta | REST | Latência p95 (ms) | 11.016,00 × 10.000,66 | < 0,001 | -1,00 (grande) | 7,8 × 0,0 | 0,017 |
| alta | REST | Throughput (req/s) | 100,02 × 123,28 | < 0,001 | 1,00 (grande) | 0,9 × 3,6 | 0,192 |
| alta | REST | Erro técnico (%) | 99,96 × 17,85 | < 0,001 | -1,00 (grande) | 2,9 × 26,6 | 0,314 |
| alta | REST | CPU total (% de 1 núcleo) | 462,8 × 439,3 | < 0,001 | -1,00 (grande) | 2,0 × 1,2 | 0,135 |
| alta | REST | Memória total (MB) | 543,8 × 520,1 | < 0,001 | -1,00 (grande) | 1,4 × 0,8 | 0,597 |
| alta | gRPC | Latência média (ms) | 7.236,83 × 5.165,17 | < 0,001 | -1,00 (grande) | 16,1 × 3,4 | 0,202 |
| alta | gRPC | Latência mediana (ms) | 6.819,45 × 5.087,53 | < 0,001 | -1,00 (grande) | 14,3 × 4,1 | 0,186 |
| alta | gRPC | Latência p95 (ms) | 10.001,01 × 6.834,23 | < 0,001 | -1,00 (grande) | 11,5 × 2,8 | 0,087 |
| alta | gRPC | Throughput (req/s) | 147,72 × 194,38 | < 0,001 | 1,00 (grande) | 10,9 × 3,3 | 0,438 |
| alta | gRPC | Erro técnico (%) | 3,02 × 0,00 | < 0,001 | -1,00 (grande) | 237,4 × 210,8 | 0,228 |
| alta | gRPC | CPU total (% de 1 núcleo) | 278,0 × 245,9 | < 0,001 | -1,00 (grande) | 8,3 × 2,4 | 0,171 |
| alta | gRPC | Memória total (MB) | 616,6 × 574,2 | < 0,001 | -1,00 (grande) | 1,9 × 0,9 | 0,091 |
| alta | Mensageria | Latência média (ms) | 9.917,22 × 6.247,61 | < 0,001 | -1,00 (grande) | 6,8 × 3,7 | 0,060 |
| alta | Mensageria | Latência mediana (ms) | 10.000,24 × 6.178,72 | < 0,001 | -1,00 (grande) | 0,7 × 3,9 | 0,013 |
| alta | Mensageria | Latência p95 (ms) | 11.117,16 × 8.042,69 | < 0,001 | -1,00 (grande) | 7,9 × 7,4 | 0,409 |
| alta | Mensageria | Throughput (req/s) | 108,68 × 162,03 | < 0,001 | 1,00 (grande) | 3,8 × 3,5 | 0,571 |
| alta | Mensageria | Erro técnico (%) | 64,97 × 0,23 | < 0,001 | -1,00 (grande) | 29,6 × 107,0 | 0,001 |
| alta | Mensageria | CPU total (% de 1 núcleo) | 327,7 × 286,5 | < 0,001 | -0,92 (grande) | 5,0 × 4,3 | 0,332 |
| alta | Mensageria | Memória total (MB) | 697,9 × 659,3 | < 0,001 | -1,00 (grande) | 2,3 × 1,5 | 0,582 |
| rampup | REST | Latência média (ms) | 6.385,53 × 4.995,74 | < 0,001 | -1,00 (grande) | 2,7 × 5,5 | 0,662 |
| rampup | REST | Latência mediana (ms) | 8.595,60 × 6.258,82 | < 0,001 | -1,00 (grande) | 7,0 × 10,5 | 0,881 |
| rampup | REST | Latência p95 (ms) | 10.902,80 × 8.712,74 | < 0,001 | -1,00 (grande) | 8,0 × 3,9 | 0,083 |
| rampup | REST | Throughput (req/s) | 104,88 × 121,92 | < 0,001 | 1,00 (grande) | 1,5 × 3,4 | 0,283 |
| rampup | REST | Erro técnico (%) | 20,64 × 0,98 | < 0,001 | -1,00 (grande) | 55,1 × 60,3 | 0,009 |
| rampup | REST | CPU total (% de 1 núcleo) | 359,8 × 333,3 | < 0,001 | -0,96 (grande) | 1,9 × 3,9 | 0,140 |
| rampup | REST | Memória total (MB) | 489,2 × 457,7 | < 0,001 | -1,00 (grande) | 2,4 × 0,8 | 0,105 |
| rampup | gRPC | Latência média (ms) | 4.461,01 × 3.147,33 | < 0,001 | -1,00 (grande) | 6,6 × 7,4 | 0,135 |
| rampup | gRPC | Latência mediana (ms) | 5.639,83 × 4.102,50 | < 0,001 | -1,00 (grande) | 8,5 × 8,9 | 0,436 |
| rampup | gRPC | Latência p95 (ms) | 8.095,49 × 5.514,57 | < 0,001 | -1,00 (grande) | 11,0 × 6,6 | 0,010 |
| rampup | gRPC | Throughput (req/s) | 133,56 × 161,57 | < 0,001 | 1,00 (grande) | 3,8 × 4,9 | 0,488 |
| rampup | gRPC | Erro técnico (%) | 0,08 × 0,00 | < 0,001 | -1,00 (grande) | 121,3 × — | 0,025 |
| rampup | gRPC | CPU total (% de 1 núcleo) | 226,7 × 192,7 | < 0,001 | -1,00 (grande) | 4,4 × 2,5 | 0,130 |
| rampup | gRPC | Memória total (MB) | 513,4 × 468,3 | < 0,001 | -1,00 (grande) | 1,8 × 0,6 | 0,257 |
| rampup | Mensageria | Latência média (ms) | 6.273,37 × 4.191,36 | < 0,001 | -1,00 (grande) | 7,7 × 3,0 | 0,016 |
| rampup | Mensageria | Latência mediana (ms) | 7.769,13 × 5.253,92 | < 0,001 | -1,00 (grande) | 9,4 × 4,5 | 0,015 |
| rampup | Mensageria | Latência p95 (ms) | 10.889,16 × 6.910,59 | < 0,001 | -1,00 (grande) | 6,5 × 2,3 | 0,021 |
| rampup | Mensageria | Throughput (req/s) | 107,01 × 139,01 | < 0,001 | 1,00 (grande) | 4,6 × 1,8 | 0,028 |
| rampup | Mensageria | Erro técnico (%) | 8,43 × 0,03 | < 0,001 | -1,00 (grande) | 93,5 × 117,4 | 0,009 |
| rampup | Mensageria | CPU total (% de 1 núcleo) | 286,2 × 249,1 | < 0,001 | -1,00 (grande) | 3,0 × 3,8 | 0,820 |
| rampup | Mensageria | Memória total (MB) | 642,7 × 581,8 | < 0,001 | -1,00 (grande) | 1,7 × 0,5 | 0,007 |

p (posição): Mann-Whitney bilateral. p (variância): Brown-Forsythe. CV: coeficiente de variação entre repetições; CV maior na nuvem com p (variância) < 0,05 sustenta a hipótese de maior variabilidade em nuvem.
