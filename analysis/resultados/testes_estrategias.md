## Comparação entre estratégias

### Ambiente local

| Cenário | Métrica | Kruskal-Wallis p | Par | Medianas | p (Holm) | δ de Cliff | Sig. |
|---|---|---|---|---|---|---|---|
| baixa | Latência média (ms) | < 0,001 | REST × gRPC | 19,90 × 16,77 | 0,012 | 0,74 (grande) | sim |
| baixa | Latência média (ms) | < 0,001 | REST × Mensageria | 19,90 × 20,71 | 0,241 | -0,32 (pequeno) | não |
| baixa | Latência média (ms) | < 0,001 | gRPC × Mensageria | 16,77 × 20,71 | 0,002 | -0,90 (grande) | sim |
| baixa | Latência mediana (ms) | < 0,001 | REST × gRPC | 19,38 × 16,34 | < 0,001 | 1,00 (grande) | sim |
| baixa | Latência mediana (ms) | < 0,001 | REST × Mensageria | 19,38 × 19,22 | 0,850 | -0,06 (desprezível) | não |
| baixa | Latência mediana (ms) | < 0,001 | gRPC × Mensageria | 16,34 × 19,22 | < 0,001 | -1,00 (grande) | sim |
| baixa | Latência p95 (ms) | 0,002 | REST × gRPC | 23,75 × 20,99 | 0,064 | 0,50 (grande) | não |
| baixa | Latência p95 (ms) | 0,002 | REST × Mensageria | 23,75 × 31,46 | 0,018 | -0,70 (grande) | sim |
| baixa | Latência p95 (ms) | 0,002 | gRPC × Mensageria | 20,99 × 31,46 | 0,008 | -0,80 (grande) | sim |
| baixa | Throughput (req/s) | 0,379 | REST × gRPC | 10,01 × 10,02 | 0,732 | -0,10 (desprezível) | não |
| baixa | Throughput (req/s) | 0,379 | REST × Mensageria | 10,01 × 10,02 | 0,555 | -0,30 (pequeno) | não |
| baixa | Throughput (req/s) | 0,379 | gRPC × Mensageria | 10,02 × 10,02 | 0,732 | -0,20 (pequeno) | não |
| baixa | Erro técnico (%) | — | REST × gRPC | 0,00 × 0,00 | 1,000 | 0,00 (desprezível) | não |
| baixa | Erro técnico (%) | — | REST × Mensageria | 0,00 × 0,00 | 1,000 | 0,00 (desprezível) | não |
| baixa | Erro técnico (%) | — | gRPC × Mensageria | 0,00 × 0,00 | 1,000 | 0,00 (desprezível) | não |
| baixa | CPU total (% de 1 núcleo) | < 0,001 | REST × gRPC | 19,2 × 16,1 | < 0,001 | 0,96 (grande) | sim |
| baixa | CPU total (% de 1 núcleo) | < 0,001 | REST × Mensageria | 19,2 × 34,1 | < 0,001 | -1,00 (grande) | sim |
| baixa | CPU total (% de 1 núcleo) | < 0,001 | gRPC × Mensageria | 16,1 × 34,1 | < 0,001 | -1,00 (grande) | sim |
| baixa | Memória total (MB) | < 0,001 | REST × gRPC | 385,0 × 405,1 | < 0,001 | -1,00 (grande) | sim |
| baixa | Memória total (MB) | < 0,001 | REST × Mensageria | 385,0 × 531,6 | < 0,001 | -1,00 (grande) | sim |
| baixa | Memória total (MB) | < 0,001 | gRPC × Mensageria | 405,1 × 531,6 | < 0,001 | -1,00 (grande) | sim |
| moderada | Latência média (ms) | 0,009 | REST × gRPC | 879,81 × 30,98 | 0,178 | 0,46 (médio) | não |
| moderada | Latência média (ms) | 0,009 | REST × Mensageria | 879,81 × 521,86 | 0,473 | -0,20 (pequeno) | não |
| moderada | Latência média (ms) | 0,009 | gRPC × Mensageria | 30,98 × 521,86 | 0,004 | -0,86 (grande) | sim |
| moderada | Latência mediana (ms) | 0,004 | REST × gRPC | 854,41 × 17,42 | 0,051 | 0,60 (grande) | não |
| moderada | Latência mediana (ms) | 0,004 | REST × Mensageria | 854,41 × 316,88 | 0,385 | -0,24 (pequeno) | não |
| moderada | Latência mediana (ms) | 0,004 | gRPC × Mensageria | 17,42 × 316,88 | 0,004 | -0,86 (grande) | sim |
| moderada | Latência p95 (ms) | 0,011 | REST × gRPC | 1.630,96 × 47,34 | 0,178 | 0,46 (médio) | não |
| moderada | Latência p95 (ms) | 0,011 | REST × Mensageria | 1.630,96 × 1.608,40 | 0,734 | -0,10 (desprezível) | não |
| moderada | Latência p95 (ms) | 0,011 | gRPC × Mensageria | 47,34 × 1.608,40 | 0,004 | -0,86 (grande) | sim |
| moderada | Throughput (req/s) | 0,003 | REST × gRPC | 98,82 × 100,02 | 0,038 | -0,60 (grande) | sim |
| moderada | Throughput (req/s) | 0,003 | REST × Mensageria | 98,82 × 98,74 | 0,405 | 0,23 (pequeno) | não |
| moderada | Throughput (req/s) | 0,003 | gRPC × Mensageria | 100,02 × 98,74 | 0,003 | 0,86 (grande) | sim |
| moderada | Erro técnico (%) | 0,040 | REST × gRPC | 0,00 × 0,00 | 0,234 | 0,30 (pequeno) | não |
| moderada | Erro técnico (%) | 0,040 | REST × Mensageria | 0,00 × 0,00 | 0,234 | 0,30 (pequeno) | não |
| moderada | Erro técnico (%) | 0,040 | gRPC × Mensageria | 0,00 × 0,00 | 1,000 | 0,00 (desprezível) | não |
| moderada | CPU total (% de 1 núcleo) | < 0,001 | REST × gRPC | 339,0 × 146,2 | 0,003 | 0,86 (grande) | sim |
| moderada | CPU total (% de 1 núcleo) | < 0,001 | REST × Mensageria | 339,0 × 275,9 | 0,571 | 0,16 (pequeno) | não |
| moderada | CPU total (% de 1 núcleo) | < 0,001 | gRPC × Mensageria | 146,2 × 275,9 | 0,003 | -0,88 (grande) | sim |
| moderada | Memória total (MB) | < 0,001 | REST × gRPC | 476,6 × 444,0 | 0,307 | 0,28 (pequeno) | não |
| moderada | Memória total (MB) | < 0,001 | REST × Mensageria | 476,6 × 584,4 | < 0,001 | -1,00 (grande) | sim |
| moderada | Memória total (MB) | < 0,001 | gRPC × Mensageria | 444,0 × 584,4 | < 0,001 | -1,00 (grande) | sim |
| alta | Latência média (ms) | < 0,001 | REST × gRPC | 10.287,91 × 7.236,83 | 0,008 | 0,80 (grande) | sim |
| alta | Latência média (ms) | < 0,001 | REST × Mensageria | 10.287,91 × 9.917,22 | 0,021 | 0,62 (grande) | sim |
| alta | Latência média (ms) | < 0,001 | gRPC × Mensageria | 7.236,83 × 9.917,22 | 0,008 | -0,80 (grande) | sim |
| alta | Latência mediana (ms) | < 0,001 | REST × gRPC | 10.000,57 × 6.819,45 | < 0,001 | 0,96 (grande) | sim |
| alta | Latência mediana (ms) | < 0,001 | REST × Mensageria | 10.000,57 × 10.000,24 | 0,003 | 0,84 (grande) | sim |
| alta | Latência mediana (ms) | < 0,001 | gRPC × Mensageria | 6.819,45 × 10.000,24 | 0,003 | -0,83 (grande) | sim |
| alta | Latência p95 (ms) | 0,005 | REST × gRPC | 11.016,00 × 10.001,01 | 0,028 | 0,66 (grande) | sim |
| alta | Latência p95 (ms) | 0,005 | REST × Mensageria | 11.016,00 × 11.117,16 | 0,273 | -0,30 (pequeno) | não |
| alta | Latência p95 (ms) | 0,005 | gRPC × Mensageria | 10.001,01 × 11.117,16 | 0,014 | -0,76 (grande) | sim |
| alta | Throughput (req/s) | < 0,001 | REST × gRPC | 100,02 × 147,72 | 0,002 | -0,90 (grande) | sim |
| alta | Throughput (req/s) | < 0,001 | REST × Mensageria | 100,02 × 108,68 | 0,010 | -0,68 (grande) | sim |
| alta | Throughput (req/s) | < 0,001 | gRPC × Mensageria | 147,72 × 108,68 | 0,003 | 0,84 (grande) | sim |
| alta | Erro técnico (%) | < 0,001 | REST × gRPC | 99,96 × 3,02 | 0,003 | 0,89 (grande) | sim |
| alta | Erro técnico (%) | < 0,001 | REST × Mensageria | 99,96 × 64,97 | 0,010 | 0,68 (grande) | sim |
| alta | Erro técnico (%) | < 0,001 | gRPC × Mensageria | 3,02 × 64,97 | 0,003 | -0,84 (grande) | sim |
| alta | CPU total (% de 1 núcleo) | < 0,001 | REST × gRPC | 462,8 × 278,0 | < 0,001 | 1,00 (grande) | sim |
| alta | CPU total (% de 1 núcleo) | < 0,001 | REST × Mensageria | 462,8 × 327,7 | < 0,001 | 1,00 (grande) | sim |
| alta | CPU total (% de 1 núcleo) | < 0,001 | gRPC × Mensageria | 278,0 × 327,7 | 0,002 | -0,82 (grande) | sim |
| alta | Memória total (MB) | < 0,001 | REST × gRPC | 543,8 × 616,6 | < 0,001 | -1,00 (grande) | sim |
| alta | Memória total (MB) | < 0,001 | REST × Mensageria | 543,8 × 697,9 | < 0,001 | -1,00 (grande) | sim |
| alta | Memória total (MB) | < 0,001 | gRPC × Mensageria | 616,6 × 697,9 | < 0,001 | -1,00 (grande) | sim |
| rampup | Latência média (ms) | < 0,001 | REST × gRPC | 6.385,53 × 4.461,01 | < 0,001 | 1,00 (grande) | sim |
| rampup | Latência média (ms) | < 0,001 | REST × Mensageria | 6.385,53 × 6.273,37 | 0,791 | 0,08 (desprezível) | não |
| rampup | Latência média (ms) | < 0,001 | gRPC × Mensageria | 4.461,01 × 6.273,37 | < 0,001 | -1,00 (grande) | sim |
| rampup | Latência mediana (ms) | < 0,001 | REST × gRPC | 8.595,60 × 5.639,83 | < 0,001 | 1,00 (grande) | sim |
| rampup | Latência mediana (ms) | < 0,001 | REST × Mensageria | 8.595,60 × 7.769,13 | 0,064 | 0,50 (grande) | não |
| rampup | Latência mediana (ms) | < 0,001 | gRPC × Mensageria | 5.639,83 × 7.769,13 | < 0,001 | -1,00 (grande) | sim |
| rampup | Latência p95 (ms) | < 0,001 | REST × gRPC | 10.902,80 × 8.095,49 | < 0,001 | 1,00 (grande) | sim |
| rampup | Latência p95 (ms) | < 0,001 | REST × Mensageria | 10.902,80 × 10.889,16 | 0,791 | 0,08 (desprezível) | não |
| rampup | Latência p95 (ms) | < 0,001 | gRPC × Mensageria | 8.095,49 × 10.889,16 | < 0,001 | -1,00 (grande) | sim |
| rampup | Throughput (req/s) | < 0,001 | REST × gRPC | 104,88 × 133,56 | < 0,001 | -1,00 (grande) | sim |
| rampup | Throughput (req/s) | < 0,001 | REST × Mensageria | 104,88 × 107,01 | 0,385 | -0,24 (pequeno) | não |
| rampup | Throughput (req/s) | < 0,001 | gRPC × Mensageria | 133,56 × 107,01 | < 0,001 | 1,00 (grande) | sim |
| rampup | Erro técnico (%) | < 0,001 | REST × gRPC | 20,64 × 0,08 | < 0,001 | 1,00 (grande) | sim |
| rampup | Erro técnico (%) | < 0,001 | REST × Mensageria | 20,64 × 8,43 | 0,038 | 0,56 (grande) | sim |
| rampup | Erro técnico (%) | < 0,001 | gRPC × Mensageria | 0,08 × 8,43 | < 0,001 | -1,00 (grande) | sim |
| rampup | CPU total (% de 1 núcleo) | < 0,001 | REST × gRPC | 359,8 × 226,7 | < 0,001 | 1,00 (grande) | sim |
| rampup | CPU total (% de 1 núcleo) | < 0,001 | REST × Mensageria | 359,8 × 286,2 | < 0,001 | 1,00 (grande) | sim |
| rampup | CPU total (% de 1 núcleo) | < 0,001 | gRPC × Mensageria | 226,7 × 286,2 | < 0,001 | -1,00 (grande) | sim |
| rampup | Memória total (MB) | < 0,001 | REST × gRPC | 489,2 × 513,4 | 0,002 | -0,84 (grande) | sim |
| rampup | Memória total (MB) | < 0,001 | REST × Mensageria | 489,2 × 642,7 | < 0,001 | -1,00 (grande) | sim |
| rampup | Memória total (MB) | < 0,001 | gRPC × Mensageria | 513,4 × 642,7 | < 0,001 | -1,00 (grande) | sim |

### Ambiente nuvem

| Cenário | Métrica | Kruskal-Wallis p | Par | Medianas | p (Holm) | δ de Cliff | Sig. |
|---|---|---|---|---|---|---|---|
| baixa | Latência média (ms) | < 0,001 | REST × gRPC | 16,65 × 13,95 | 0,006 | 0,80 (grande) | sim |
| baixa | Latência média (ms) | < 0,001 | REST × Mensageria | 16,65 × 16,51 | 0,520 | 0,18 (pequeno) | não |
| baixa | Latência média (ms) | < 0,001 | gRPC × Mensageria | 13,95 × 16,51 | < 0,001 | -1,00 (grande) | sim |
| baixa | Latência mediana (ms) | < 0,001 | REST × gRPC | 16,39 × 13,82 | 0,006 | 0,80 (grande) | sim |
| baixa | Latência mediana (ms) | < 0,001 | REST × Mensageria | 16,39 × 15,73 | 0,006 | 0,80 (grande) | sim |
| baixa | Latência mediana (ms) | < 0,001 | gRPC × Mensageria | 13,82 × 15,73 | < 0,001 | -1,00 (grande) | sim |
| baixa | Latência p95 (ms) | < 0,001 | REST × gRPC | 18,20 × 15,20 | < 0,001 | 1,00 (grande) | sim |
| baixa | Latência p95 (ms) | < 0,001 | REST × Mensageria | 18,20 × 20,56 | 0,140 | -0,40 (médio) | não |
| baixa | Latência p95 (ms) | < 0,001 | gRPC × Mensageria | 15,20 × 20,56 | < 0,001 | -1,00 (grande) | sim |
| baixa | Throughput (req/s) | 0,060 | REST × gRPC | 10,00 × 10,02 | 0,075 | -0,50 (grande) | não |
| baixa | Throughput (req/s) | 0,060 | REST × Mensageria | 10,00 × 10,01 | 0,693 | -0,10 (desprezível) | não |
| baixa | Throughput (req/s) | 0,060 | gRPC × Mensageria | 10,02 × 10,01 | 0,127 | 0,40 (médio) | não |
| baixa | Erro técnico (%) | — | REST × gRPC | 0,00 × 0,00 | 1,000 | 0,00 (desprezível) | não |
| baixa | Erro técnico (%) | — | REST × Mensageria | 0,00 × 0,00 | 1,000 | 0,00 (desprezível) | não |
| baixa | Erro técnico (%) | — | gRPC × Mensageria | 0,00 × 0,00 | 1,000 | 0,00 (desprezível) | não |
| baixa | CPU total (% de 1 núcleo) | < 0,001 | REST × gRPC | 16,7 × 14,1 | 0,003 | 0,80 (grande) | sim |
| baixa | CPU total (% de 1 núcleo) | < 0,001 | REST × Mensageria | 16,7 × 29,8 | < 0,001 | -1,00 (grande) | sim |
| baixa | CPU total (% de 1 núcleo) | < 0,001 | gRPC × Mensageria | 14,1 × 29,8 | < 0,001 | -1,00 (grande) | sim |
| baixa | Memória total (MB) | < 0,001 | REST × gRPC | 353,6 × 372,3 | < 0,001 | -1,00 (grande) | sim |
| baixa | Memória total (MB) | < 0,001 | REST × Mensageria | 353,6 × 499,2 | < 0,001 | -1,00 (grande) | sim |
| baixa | Memória total (MB) | < 0,001 | gRPC × Mensageria | 372,3 × 499,2 | < 0,001 | -1,00 (grande) | sim |
| moderada | Latência média (ms) | < 0,001 | REST × gRPC | 16,75 × 14,53 | 0,006 | 0,80 (grande) | sim |
| moderada | Latência média (ms) | < 0,001 | REST × Mensageria | 16,75 × 17,86 | 0,427 | -0,22 (pequeno) | não |
| moderada | Latência média (ms) | < 0,001 | gRPC × Mensageria | 14,53 × 17,86 | < 0,001 | -1,00 (grande) | sim |
| moderada | Latência mediana (ms) | < 0,001 | REST × gRPC | 16,30 × 14,49 | 0,006 | 0,80 (grande) | sim |
| moderada | Latência mediana (ms) | < 0,001 | REST × Mensageria | 16,30 × 15,52 | 0,006 | 0,78 (grande) | sim |
| moderada | Latência mediana (ms) | < 0,001 | gRPC × Mensageria | 14,49 × 15,52 | < 0,001 | -1,00 (grande) | sim |
| moderada | Latência p95 (ms) | < 0,001 | REST × gRPC | 19,16 × 16,18 | 0,006 | 0,80 (grande) | sim |
| moderada | Latência p95 (ms) | < 0,001 | REST × Mensageria | 19,16 × 35,56 | 0,140 | -0,40 (médio) | não |
| moderada | Latência p95 (ms) | < 0,001 | gRPC × Mensageria | 16,18 × 35,56 | < 0,001 | -1,00 (grande) | sim |
| moderada | Throughput (req/s) | 0,018 | REST × gRPC | 100,01 × 100,02 | 0,030 | -0,50 (grande) | sim |
| moderada | Throughput (req/s) | 0,018 | REST × Mensageria | 100,01 × 100,00 | 0,774 | -0,08 (desprezível) | não |
| moderada | Throughput (req/s) | 0,018 | gRPC × Mensageria | 100,02 × 100,00 | 0,015 | 0,60 (grande) | sim |
| moderada | Erro técnico (%) | 0,126 | REST × gRPC | 0,00 × 0,00 | 0,504 | 0,20 (pequeno) | não |
| moderada | Erro técnico (%) | 0,126 | REST × Mensageria | 0,00 × 0,00 | 0,504 | 0,20 (pequeno) | não |
| moderada | Erro técnico (%) | 0,126 | gRPC × Mensageria | 0,00 × 0,00 | 1,000 | 0,00 (desprezível) | não |
| moderada | CPU total (% de 1 núcleo) | < 0,001 | REST × gRPC | 136,3 × 107,9 | 0,006 | 0,80 (grande) | sim |
| moderada | CPU total (% de 1 núcleo) | < 0,001 | REST × Mensageria | 136,3 × 144,1 | 0,140 | -0,40 (médio) | não |
| moderada | CPU total (% de 1 núcleo) | < 0,001 | gRPC × Mensageria | 107,9 × 144,1 | < 0,001 | -1,00 (grande) | sim |
| moderada | Memória total (MB) | < 0,001 | REST × gRPC | 408,9 × 411,1 | 0,473 | -0,20 (pequeno) | não |
| moderada | Memória total (MB) | < 0,001 | REST × Mensageria | 408,9 × 541,8 | < 0,001 | -1,00 (grande) | sim |
| moderada | Memória total (MB) | < 0,001 | gRPC × Mensageria | 411,1 × 541,8 | < 0,001 | -1,00 (grande) | sim |
| alta | Latência média (ms) | < 0,001 | REST × gRPC | 8.401,96 × 5.165,17 | < 0,001 | 1,00 (grande) | sim |
| alta | Latência média (ms) | < 0,001 | REST × Mensageria | 8.401,96 × 6.247,61 | < 0,001 | 1,00 (grande) | sim |
| alta | Latência média (ms) | < 0,001 | gRPC × Mensageria | 5.165,17 × 6.247,61 | < 0,001 | -1,00 (grande) | sim |
| alta | Latência mediana (ms) | < 0,001 | REST × gRPC | 8.168,91 × 5.087,53 | < 0,001 | 1,00 (grande) | sim |
| alta | Latência mediana (ms) | < 0,001 | REST × Mensageria | 8.168,91 × 6.178,72 | < 0,001 | 1,00 (grande) | sim |
| alta | Latência mediana (ms) | < 0,001 | gRPC × Mensageria | 5.087,53 × 6.178,72 | < 0,001 | -1,00 (grande) | sim |
| alta | Latência p95 (ms) | < 0,001 | REST × gRPC | 10.000,66 × 6.834,23 | < 0,001 | 1,00 (grande) | sim |
| alta | Latência p95 (ms) | < 0,001 | REST × Mensageria | 10.000,66 × 8.042,69 | < 0,001 | 1,00 (grande) | sim |
| alta | Latência p95 (ms) | < 0,001 | gRPC × Mensageria | 6.834,23 × 8.042,69 | < 0,001 | -1,00 (grande) | sim |
| alta | Throughput (req/s) | < 0,001 | REST × gRPC | 123,28 × 194,38 | < 0,001 | -1,00 (grande) | sim |
| alta | Throughput (req/s) | < 0,001 | REST × Mensageria | 123,28 × 162,03 | < 0,001 | -1,00 (grande) | sim |
| alta | Throughput (req/s) | < 0,001 | gRPC × Mensageria | 194,38 × 162,03 | < 0,001 | 1,00 (grande) | sim |
| alta | Erro técnico (%) | < 0,001 | REST × gRPC | 17,85 × 0,00 | < 0,001 | 1,00 (grande) | sim |
| alta | Erro técnico (%) | < 0,001 | REST × Mensageria | 17,85 × 0,23 | < 0,001 | 1,00 (grande) | sim |
| alta | Erro técnico (%) | < 0,001 | gRPC × Mensageria | 0,00 × 0,23 | < 0,001 | -0,88 (grande) | sim |
| alta | CPU total (% de 1 núcleo) | < 0,001 | REST × gRPC | 439,3 × 245,9 | < 0,001 | 1,00 (grande) | sim |
| alta | CPU total (% de 1 núcleo) | < 0,001 | REST × Mensageria | 439,3 × 286,5 | < 0,001 | 1,00 (grande) | sim |
| alta | CPU total (% de 1 núcleo) | < 0,001 | gRPC × Mensageria | 245,9 × 286,5 | < 0,001 | -1,00 (grande) | sim |
| alta | Memória total (MB) | < 0,001 | REST × gRPC | 520,1 × 574,2 | < 0,001 | -1,00 (grande) | sim |
| alta | Memória total (MB) | < 0,001 | REST × Mensageria | 520,1 × 659,3 | < 0,001 | -1,00 (grande) | sim |
| alta | Memória total (MB) | < 0,001 | gRPC × Mensageria | 574,2 × 659,3 | < 0,001 | -1,00 (grande) | sim |
| rampup | Latência média (ms) | < 0,001 | REST × gRPC | 4.995,74 × 3.147,33 | < 0,001 | 1,00 (grande) | sim |
| rampup | Latência média (ms) | < 0,001 | REST × Mensageria | 4.995,74 × 4.191,36 | < 0,001 | 0,92 (grande) | sim |
| rampup | Latência média (ms) | < 0,001 | gRPC × Mensageria | 3.147,33 × 4.191,36 | < 0,001 | -1,00 (grande) | sim |
| rampup | Latência mediana (ms) | < 0,001 | REST × gRPC | 6.258,82 × 4.102,50 | < 0,001 | 1,00 (grande) | sim |
| rampup | Latência mediana (ms) | < 0,001 | REST × Mensageria | 6.258,82 × 5.253,92 | 0,003 | 0,80 (grande) | sim |
| rampup | Latência mediana (ms) | < 0,001 | gRPC × Mensageria | 4.102,50 × 5.253,92 | < 0,001 | -1,00 (grande) | sim |
| rampup | Latência p95 (ms) | < 0,001 | REST × gRPC | 8.712,74 × 5.514,57 | < 0,001 | 1,00 (grande) | sim |
| rampup | Latência p95 (ms) | < 0,001 | REST × Mensageria | 8.712,74 × 6.910,59 | < 0,001 | 1,00 (grande) | sim |
| rampup | Latência p95 (ms) | < 0,001 | gRPC × Mensageria | 5.514,57 × 6.910,59 | < 0,001 | -1,00 (grande) | sim |
| rampup | Throughput (req/s) | < 0,001 | REST × gRPC | 121,92 × 161,57 | < 0,001 | -1,00 (grande) | sim |
| rampup | Throughput (req/s) | < 0,001 | REST × Mensageria | 121,92 × 139,01 | < 0,001 | -1,00 (grande) | sim |
| rampup | Throughput (req/s) | < 0,001 | gRPC × Mensageria | 161,57 × 139,01 | < 0,001 | 1,00 (grande) | sim |
| rampup | Erro técnico (%) | < 0,001 | REST × gRPC | 0,98 × 0,00 | < 0,001 | 0,90 (grande) | sim |
| rampup | Erro técnico (%) | < 0,001 | REST × Mensageria | 0,98 × 0,03 | 0,004 | 0,83 (grande) | sim |
| rampup | Erro técnico (%) | < 0,001 | gRPC × Mensageria | 0,00 × 0,03 | 0,004 | -0,70 (grande) | sim |
| rampup | CPU total (% de 1 núcleo) | < 0,001 | REST × gRPC | 333,3 × 192,7 | < 0,001 | 1,00 (grande) | sim |
| rampup | CPU total (% de 1 núcleo) | < 0,001 | REST × Mensageria | 333,3 × 249,1 | < 0,001 | 1,00 (grande) | sim |
| rampup | CPU total (% de 1 núcleo) | < 0,001 | gRPC × Mensageria | 192,7 × 249,1 | < 0,001 | -1,00 (grande) | sim |
| rampup | Memória total (MB) | < 0,001 | REST × gRPC | 457,7 × 468,3 | < 0,001 | -1,00 (grande) | sim |
| rampup | Memória total (MB) | < 0,001 | REST × Mensageria | 457,7 × 581,8 | < 0,001 | -1,00 (grande) | sim |
| rampup | Memória total (MB) | < 0,001 | gRPC × Mensageria | 468,3 × 581,8 | < 0,001 | -1,00 (grande) | sim |

δ de Cliff > 0: a primeira estratégia do par tem valores maiores. Significativo: p ajustado por Holm < 0,05.
