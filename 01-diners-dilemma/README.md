# 01 · Diner's Dilemma: peer-swap detection

*Lead: Siva Kumar Lakkoju ([@sivakumarlakkoju](https://github.com/sivakumarlakkoju)). Part of [Noticing the Move, Missing the Player](../README.md).*

Can LLM agents notice that a peer in a repeated Diner's Dilemma has been silently replaced by a
different model?

**Setup.**
- Agents play on the [Shi et al. (2026) harness](https://github.com/Jerick-1380/LLM-Trust-Breaking):
  private plan, then public announcement, then action, then trust rating and note.
- Seat Q is handed to another model partway through the game. The swapped-in model keeps the seat
  name and is not told.
- Every condition branches from the same pre-swap history.

| Folder | What it is |
|---|---|
| [`collusion_peer/`](collusion_peer) | The main Diner's Dilemma experiment. It contains:<ul><li>the [`experiment/`](collusion_peer/experiment) code</li><li>the patched harness</li><li>runs</li><li>the results notes: [`PILOT_RESULTS.md`](collusion_peer/PILOT_RESULTS.md) and [`Memory_Diner_Results.md`](collusion_peer/Memory_Diner_Results.md)</li></ul> |
| [`peer_swap/`](peer_swap) | Signal Ring: three colluders hide targets from a monitor in table talk, and one colluder is silently swapped |

Start with [`collusion_peer/README.md`](collusion_peer/README.md) for setup and commands. API keys
go in `harness/.env`, which is git-ignored; copy `harness/.env.example` to create it.
