package br.com.stocksense.client

import br.com.stocksense.client.dto.PredictRequest
import br.com.stocksense.client.dto.PredictResponse
import org.springframework.cloud.openfeign.FeignClient
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestBody

@FeignClient(name = "ml-service", url = "\${ml.service.url}")
interface MlServiceClient {

    @PostMapping("/predict")
    fun predict(@RequestBody request: PredictRequest): PredictResponse

    @GetMapping("/health")
    fun health(): Map<String, String>
}
