# COMPETITIVE MATRIX — WorkAttest

> **Proof before acceptance.**

Onde WorkAttest se distingue. **Princípio de posicionamento:** WorkAttest **não**
compete como editor, agente, framework de agentes, observabilidade, SIEM, GRC genérico,
gestor de projetos, ferramenta de testes ou IAM. É uma **camada neutra** entre eles.

---

## 1. O eixo de diferenciação

A maioria das ferramentas prova **fragmentos**:

- um agente chamou uma ferramenta;
- um utilizador iniciou uma sessão;
- uma policy permitiu uma ação;
- um commit passou no CI.

WorkAttest prova **adicionalmente** que:

- o commit corresponde ao **pedido autorizado**;
- os artefactos concretos estão identificados;
- os checks aplicáveis foram executados (e o agente não os escolheu);
- a evidência pertence àquela versão;
- **nenhuma obrigação foi omitida**;
- a pessoa responsável aceitou **exatamente** aquele resultado;
- o receipt continua verificável **fora** do WorkAttest.

## 2. Matriz por categoria

Legenda: ✅ cobre · ◐ parcial · ✗ não cobre · — fora de âmbito da categoria

| Capacidade | Coding agents (Claude/Codex/Cursor) | Observabilidade / traces | SIEM | CI/CD + status checks | Supply-chain (Sigstore/in-toto/SLSA) | GitHub Artifact Attestations | GRC genérico | **WorkAttest** |
|---|---|---|---|---|---|---|---|---|
| Produzir a alteração | ✅ | ✗ | ✗ | ◐ | ✗ | ✗ | ✗ | — (integra) |
| Registar o que aconteceu | ◐ | ✅ | ✅ | ◐ | ✗ | ✗ | ◐ | ◐ (foco no aceite) |
| Autorização com âmbito **antes** da ação | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ◐ | ✅ |
| Provar que os checks **correram** | ✗ | ✗ | ✗ | ◐ | ◐ | ◐ | ✗ | ✅ |
| Agente **não** escolhe os checks | ✗ | — | — | ✗ | — | — | ✗ | ✅ |
| Proveniência do artefacto (hash) | ✗ | ✗ | ✗ | ◐ | ✅ | ✅ | ✗ | ✅ |
| **Aprovação humana ligada ao artefacto exato** | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ◐ | ✅ |
| "Nenhuma obrigação omitida" (completude da policy) | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ◐ | ✅ |
| Verificação **offline** por terceiro | ✗ | ✗ | ✗ | ✗ | ◐ | ◐ | ✗ | ✅ |
| Neutro entre stacks/agentes | — | ◐ | ◐ | ✗ | ✅ | ✗ | ◐ | ✅ |

## 3. Concorrentes de fronteira (os que mais se aproximam)

| Concorrente | Sobreposição | Delta do WorkAttest | Risco |
|---|---|---|---|
| **GitHub Artifact Attestations** | Proveniência de build assinada, verificável | Não modela *autorização prévia* nem *aprovação humana do resultado exato* como aceitação formal | **Alto** — incumbente pode estender-se; mitigar integrando, não competindo |
| **Sigstore + in-toto + SLSA** | Assinatura, atestação, níveis de proveniência | WorkAttest **alinha-se** e acrescenta a camada de *trabalho aceite* (policy + approval + custódia) | Médio — mais aliado que rival; usar como base |
| **Observabilidade de agentes** (LLM tracing) | Regista tool calls e sessões | Trace ≠ cadeia de custódia verificável nem aceitação assinada | Baixo — complementar |
| **GRC / audit tooling** | Workflow de aprovação e evidência | Aprovação declarativa vs. aprovação ligada criptograficamente ao artefacto | Médio — vender como camada de prova sob o GRC |

## 4. Posicionamento de uma frase

> Sigstore/SLSA provam **de onde veio o artefacto**. WorkAttest prova **que aquele
> trabalho foi autorizado, verificado e aceite pela pessoa responsável** — e liga isso
> ao artefacto exato, verificável offline.

## 5. Implicações estratégicas

1. **Integrar, não competir**, com identidade/IAM e proveniência de build.
2. O fosso defensável é a **aceitação com custódia** (autorização + policy + approval
   humano ligado ao artefacto), não a assinatura em si.
3. O risco competitivo mais real é um incumbente (GitHub) estender-se ao "aceite".
   Contramedida: profundidade no primeiro wedge + neutralidade entre stacks + valor
   para auditoria antes que o incumbente lá chegue.

## 6. Ligações

- Decisões de standards que sustentam a interop: `docs/STANDARDS-DECISIONS.md`.
- O que exatamente se prova: `docs/ACCOUNTABILITY-MODEL.md`.
