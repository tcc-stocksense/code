package br.com.stocksense

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.cloud.openfeign.EnableFeignClients

@SpringBootApplication
@EnableFeignClients
class StockSenseApplication

fun main(args: Array<String>) {
    runApplication<StockSenseApplication>(*args)
}