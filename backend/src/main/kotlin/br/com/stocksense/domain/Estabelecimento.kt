package br.com.stocksense.domain

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.Table

@Entity
@Table(name = "estabelecimento")
class Estabelecimento(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Int = 0,

    @Column(name = "nome_fantasia", nullable = false, length = 100)
    var nomeFantasia: String,

    @Column(length = 18)
    var cnpj: String? = null,

    @Column(length = 200)
    var endereco: String? = null,

    @Column(nullable = false, length = 100, unique = true)
    var email: String,

    @Column(name = "senha_hash", nullable = false, length = 255)
    var senhaHash: String,
)
