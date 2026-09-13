# MinecraftGuess — POC de mídia

Data: 2026-09

Fonte de mídia:
Minecraft Wiki

Método:
URLs MediaWiki Special:Redirect/file

## Entidades testadas

| Tipo | Entidade | Página Wiki | Arquivo | HTTP | Browser | Observação |
|---|---|---|---|---|---|---|
| mob | Cow | ... | ... | 200 | OK | ... |
| biome | Plains | ... | ... | 200 | OK | ... |
| item | Diamond Sword | ... | ... | 200 | OK | ... |
| structure | Stronghold | ... | ... | 200 | OK | ... |
| enchantment | Sharpness | ... | ... | 200/null | OK/fallback | ... |

## Resultado

- a Wiki pode fornecer mídia sem participar do fluxo de partida;
- as URLs são resolvidas previamente;
- nenhuma consulta à Wiki precisa ocorrer quando o usuário joga;
- ausência de imagem não impede o funcionamento da partida.
