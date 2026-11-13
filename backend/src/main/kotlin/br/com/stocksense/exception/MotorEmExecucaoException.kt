package br.com.stocksense.exception

/**
 * Já existe um lote do motor em andamento para o estabelecimento.
 *
 * Mapeada para `409 Conflict` — não é erro do cliente nem falha do sistema, é
 * concorrência legítima: o recálculo pedido não cabe agora porque outro está rodando.
 */
class MotorEmExecucaoException(message: String) : RuntimeException(message)
