# JarvisAI — Serviços Auxiliares (Java)

Este diretório reserva o espaço para serviços auxiliares desacoplados
do backend Python, úteis para expansões futuras que se beneficiem de
concorrência/paralelismo nativo da JVM ou de integração com hardware
específico (ex.: comunicação serial com dispositivos IoT).

## Por que Java aqui?

O núcleo de IA (intents, memória, plugins) permanece 100% em Python,
que é o ambiente mais produtivo para NLP e integração de bibliotecas.
Java entra apenas onde a JVM tem vantagem real: processamento paralelo
pesado, sockets de longa duração, ou monitoramento de dispositivos
externos — sempre como um **serviço independente**, nunca importado
diretamente pelo Python.

## Comunicação com o backend Python

A integração acontece por **socket TCP simples** (ver `EchoService.java`),
mantendo o desacoplamento total: o Python enxerga o serviço Java como
qualquer outro serviço de rede, via `socket` da biblioteca padrão.

## Como executar o serviço de exemplo

```bash
cd java-services/src
javac EchoService.java
java EchoService
```

O serviço sobe na porta `9090` e ecoa mensagens recebidas — um ponto de
partida para implementar serviços reais (ex.: um monitor de dispositivos
USB, ou um processador de tarefas em lote).
