package br.com.stocksense

import br.com.stocksense.config.JwtConfig
import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.context.properties.EnableConfigurationProperties
import org.springframework.boot.runApplication
import org.springframework.cloud.openfeign.EnableFeignClients

@SpringBootApplication
@EnableFeignClients
@EnableConfigurationProperties(JwtConfig::class)
class StockSenseApplication

fun main(args: Array<String>) {
    runApplication<StockSenseApplication>(*args)
}