
## **Core principles - What is TDD? What are Red, Green, and Refactor?**
Test-Driven Development is a programming style where you break desired behaviors into small goals, choose one, write a test that specifies that behavior, implement only enough code to make the test pass, then refactor the design while keeping the test passing, and repeat.

### Red, Green, Refactor cycle
is the core of the TDD process, after listing out what are the test scenarios you want to cover, you:
- In the red phase, select one item on the list into an actual, concrete, runnable test, confirm the test fails as the proof of its ability to flag missing or unwanted behaviors.
- In the green phase, write a simple implementation code until the test passes, along side all previous tests.
- In the refactor phase we improve the code's structure, abstraction and remove duplicates, without changing the behavior, the test would aid us in ensuring the original behavior intact.

After the refactor step, we add more test scenario into the list if discovered any, and move to the next behavior, begin a new cycle.

### Extra:
- You dont have to know the **entired** architecture or all future tests beforehand. The code follows TDD is inherently increasing its feature one at a time, so you can adding more if discovered any.
- Prefer picking a **small but meaningful** piece of the requirement that moves the implementation forward first.
- Testing in TDD is the mechanism that drives implementation.
- Each circle is a small a feedback loop to move foward to the final goal - and human love small, achievable goals.

### Differences of TDD and ordinary development cycle with testing
**Flow of an ordinary development cycle with tests**
```
Understand requirements
    ↓
Design data structures / architecture
    ↓
Implement priority system
    ↓
Implement edge cases
    ↓
Write tests
    ↓
Fix problems
    ↓
Refactor
```

**Flow of TDD**
```
Understand requirement
    ↓
List possible behaviors
    ↓
Choose one small behavior
    ↓
Write test
    ↓
Red phase
    ↓
Implement minimum code
    ↓
Green phase
    ↓
Refactor
    ↓
Choose next behavior
    ↓
Repeat
```

- In ordinary development cycle, testing is a tool for verification and assuring quality of implemetation, meanwhile in TDD it act as a design tool, a small stair step toward the goal that drive implementation.
- TDD give you quicker feedback, better at detecting regression problems because problems surface faster and closer to where the changes happen.
- In TDD, tests are built before and during the development process while in ordinary cycle test suits are built alongside/after the implementation.
- TDD provides tight feedback mechanism for incremental implementation and design. Choose ordinary development allow exploration upfront before test exists.
- TDD cost more initial development effort than ordinary developing method for tests preparation.
- Refactoring in TDD is essentional and can be done in small unit and generally safer with the confirmation from tests. 


## **Testing levels**

### Difference between unit tests, integration tests, and end-to-end tests
Validate algorithmic correctness and edge cases.Verify data contracts, API schemas, and communication.Validate the complete user journey and infrastructure health.
|                       | **Unit test** | **Integration test** | **End-to-end test** |
| --------------------- | ------------------------ | --------------------------------- | --------------------------------------------------- |
| **Main usage**        | Validate algorithmic correctness and edge case | Verify data contracts, API schemas, and communication | Validate the complete user journey and infrastructure health. |
| **Main question**     | Does this **part** work? | Do these **parts work together**? | Does the **whole system** work for a real scenario? |
| **Scope**             | Small, isolated unit     | Multiple connected components     | Entire application/system |
| **Dependencies**      | Usually replaced/mocked  | Some real dependencies            | Mostly real system |
| **Speed**             | Usually fastest          | Medium                            | Usually slowest |
| **Failure diagnosis** | Usually easiest          | Harder                            | Hardest |

### Example of tests for a Ticket Manager CLI
For a simple Ticket Manager CLI that support:
```python
ticket add "Printer is broken"
ticket list
ticket close 3
ticket show 3
```
**Unit Test**
```python
def test_new_ticket_is_open():
    ticket = Ticket.create("Printer is broken")

    assert ticket.status == "open"
```
Testing one single behavior of opening a new ticket `ticket add` to see if working properly (the status should be open)

**Intergration test**
```python
def test_ticket_repository_saves_and_loads_ticket(tmp_path):
    db = TicketDatabase(tmp_path / "test.db")
    repo = TicketRepository(db)

    ticket = Ticket.create("Printer is broken")
    repo.save(ticket)

    loaded = repo.get(ticket.id)

    assert loaded.title == "Printer is broken"
    assert loaded.status == "open"
```

Testing to save and load a ticket from database

**End-to-End Test**
```python
def test_user_can_create_and_close_ticket():
    run_cli(["add", "Printer is broken"])

    run_cli(["close", "1"])

    result = run_cli(["show", "1"])

    assert "Printer is broken" in result
    assert "closed" in result
```

with `run_cli()` launch the real application to test a workflow as a real user

## **AI validation - How tests help verify and improve AI-generated code**

### Common flaws of AI generated code and how testing in generate help with that

| AI-generated code weakness | What is it? | Why does it happen? | How testing helps |
| ---------------------------------------- | ------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| **Incorrect logic** | Code produces the wrong result despite looking reasonable | The AI generates code from trained patterns rather than actually executing a reliable reasoning process against real requirements | Tests provide concrete expected outcomes |
| **Misunderstood requirements** | Implementation solves a subtly different problem from the one intended | Natural-language requirements are often incomplete/ambiguous, and the AI must infer missing intent from context | Tests turn important requirements into explicit, executable specifications |
| **Missing edge cases** | Normal cases work, unusual inputs fail | The prompt may not mention the edge case, and the AI cannot guarantee that it has identified every relevant boundary condition | Explicit edge-case tests force those conditions to be considered |
| **Wrong assumptions about dependencies** | Code assumes an API, library, database, or component behaves differently from reality | The AI may rely on patterns, outdated knowledge, or incomplete project context rather than the actual environment | Integration tests exercise the real interfaces |
| **Integration errors** | Individual pieces look correct but fail when connected | The AI generates components based on local context; it may not correctly understand all contracts between existing components | Integration tests verify the actual interactions |
| **Security vulnerabilities** | Generated code contains unsafe patterns or fails to enforce security requirements | Training data contains both secure and insecure code, while security requirements are often unstated or require specialized reasoning | Security tests/scanners can detect known classes of weaknesses |
| **Regression after changes** | A new AI-generated change breaks previously working behavior | AI generates the requested modification without necessarily understanding all downstream effects of changing existing code | Regression tests preserve previously established behavior |
| **Unnecessary complexity** | Code works but contains needless abstractions, dependencies, or complicated logic | AI tends to generate plausible conventional solutions from patterns in its training data; the simplest solution isn't necessarily what it produces | Tests make refactoring safer, allowing complexity to be removed while checking behavior remains intact |
| **Hallucinated/nonexistent/outdated APIs** | Code calls functions, parameters, or libraries that don't actually exist/outdated | The model predicts likely code based on learned patterns; it doesn't inherently have authoritative knowledge of the exact installed environment | Tests immediately expose calls that cannot execute; type/static checks can catch some before runtime |
| **Overfitting to the prompt/example** | Code works for the demonstrated example but fails for the broader requirement | The model may optimize its response around the examples/context supplied rather than a complete specification | Multiple tests define a broader behavioral boundary |
| **Performance problems** | Generate code is functionally correct but too slow or resource-heavy at real-world scale | Multiple correct implementations exist and the AI is not guarantee of picking the efficient one, it also has no or limited infomationa about actual product's contexts | Performance tests or benchmarks help in verify the speed of a result |

### How TDD helps in control the AI-generated implemetation
TDD helps control AI-generated implementation by defining the expected behavior before asking AI to implement it.
It creates a separation of concerns:
- We define the expect behavior and edge cases first before ask the AI for how to implement it.
- Regression tests make sure previously established behavior is preserved when the AI modifies later codes.
- We can confirm it worked before refining, refactoring the code.

## **CLI testing - What should be tested in a CLI tool: commands, validation, file storage, and errors**
### What to be tested in a CLI tool in general
|                            | What to test                     | Reason |
| -------------------------- | -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Command parsing**        | Commands, arguments, options     | Invalid/missing CLI input should be handled correctly. |
| **Output**                 | Messages, displayed data         | Output is part of the user's interface. |
| **Exit behavior**          | Success/failure exit codes       | Scripts and other programs may depend on exit status. |
| **Input/errors**           | Invalid input, missing resources | CLI users commonly encounter errors through textual input. |
| **stdin/prompts**          | Interactive input, if used       | The CLI may need to behave correctly with user input. |
| **Filesystem/environment** | Files, paths, environment        | CLI programs frequently interact directly with the filesystem. |
| **End-to-end commands**    | Actual command > result          | Verifies that the pieces work together. |

## **Common mistakes**

### Common tactical mistakes
- Poorly picking a too big goal, can be avoid by breaking the requirement into one observable behaviors. Reconsidering whether the behavior is too large if the test is becoming complicated.
- Writing too many tests before coding - avoid fully specify the feature upfront, pick the next behavior, test it, implement it, and reassess what comes next.
- Testing implementation details, avoid by staying in testing observable behavior and interfaces, not internal function calls, private fields, or specific algorithms unless those details themselves are requirements.
- Forget to maintain the test suite - keep most tests fast and focused, remove obsolete tests, fix flaky tests immediately; separate slower integration/E2E tests from the fast feedback loop.
- TDD doesn't fit the problem well - be flexible, if problem required exploration, try first.
- Forgetting Refactor / Refactor too early - refactor is crucial in TDD but should be done once the behavior is passed with test.

### Common technical mistakes
Mistakes in details of the developing process, avoid by awareness and experience

| Micro mistake                      | Avoid / mitigate                                                        | Practical check                                                 |
| ---------------------------------- | ----------------------------------------------------------------------- | --------------------------------------------------------------- |
| **Missing assertion**              | Require every behavior test to have a meaningful verification           | “What exactly am I proving?”                                    |
| **Weak assertion**                 | Assert the actual expected behavior, not merely existence/type/non-null | `assert result == 5`, not `assert result is not None`           |
| **Wrong expected value**           | Derive expected results independently from the implementation           | Don't copy the implementation's calculation into the test       |
| **Incomplete assertion**           | Cover every important observable outcome of the behavior                | “What else should be true after this operation?”                |
| **Overly broad assertion**         | Assert only behavior relevant to the test                               | Avoid comparing an entire object when only one property matters |
| **Wrong test setup**               | Make inputs explicitly represent the intended scenario                  | Read the test as a real example of the requirement              |
| **Happy-path only**                | Add important boundary/error cases                                      | Empty, zero, maximum, invalid input, failure, etc.              |
| **Testing implementation details** | Assert outputs/state/observable effects instead of internal mechanics   | Ask “what happened?” rather than “which method was called?”     |
| **Test passes for wrong reason**   | Intentionally break the implementation and verify the test goes Red     | Mutation testing is especially useful here                      |
| **Hidden shared state**            | Reset state and keep tests independent                                  | A test should work when run alone                               |
| **Order dependency**               | Don't rely on another test running first                                | Randomize test order if possible                                |
| **Flaky timing/concurrency**       | Control time, randomness, external resources where appropriate          | Inject a clock/random source rather than sleeping               |
| **Over-mocking**                   | Mock only boundaries that genuinely need isolation                      | Prefer real simple objects when practical                       |
| **Duplicate tests**                | Remove tests that provide no additional failure detection               | Each test should add meaningful coverage                        |
| **Unreadable test**                | Make the scenario and expected behavior obvious                         | Arrange → Act → Assert                                          |

## **Workflow application evidences**

### Chat links
Here are the chat I used during the research progress
1. [TDD Explaination](https://chatgpt.com/share/6ab8b549-845c-83ec-a35f-dec2f4d4ebcf)
2. [Explore about tests](https://chatgpt.com/share/6ab8b55e-e3a4-83ec-b3fa-c17a3a8e53d2)
3. [Ticket Manager CLI Plan](https://chatgpt.com/share/6ab8b521-3c3c-83ec-bc5d-0347f93eba5d)

For personal review purpose and convinience of giving you a sumup of what I did, I branched the chat and asked this as the final prompt
```
In this chat, did I apply any of this workflow? Choosing strong and clear applications, and show me the structure. What could I improve?
1. **Layered Questioning** - Research → Brief → Example → Validation
2. **Solution Exploration** - Explore options → Compare pros/cons → Choose with context
3. **Iterative Refinement** - Review AI suggestions → Refine → Feedback → Validate
```
**Im also aware that I still need to tighten validation control than this when working with other AI because ChatGPT's Dreaming did really a good job of making good assumptions and remembered my preferred research structuring style. Which might not be the case for other AI**

### Layered questioning:

- **Research**
what is TDD in programming? What is the main idea behind it? Explain it to me like I'm 5, then explain it to me again like I'm a developer. For definition, determine reliable sources as references

- **Brief / refine**
"So my understanding is...?"

- **Example / mental model**
"Does it require meta awareness?"

- **Validation**
"How is it different from ordinary development?"

### Solutions exploration

- **Explore options / Compare pro-con / Add context**
This is a small project, is there an alternative way to store this? What are the risks? Best, worst-case scenario, and likelihood of those risk? I want to be...

- **Choose with context / Expand pro-con**
...update our options set. With such options, what worth keeping an eye on when selecting JSON as the storage? What are the risks? Best, worst-case scenario, and likelihood of those risk?

### Iterative Refinement
Q: Summarize the similarity, difference between unit, integration, and end-to-end tests?
- **Review AI suggestions:**
AI presented the answer that mix up the importance (primary definion and secondary properties) to tell 3 type of tests apart, to clear up what I could learn, I followed up with:

Q: So, as I understand the only core difference that the developer is trying to find out is the main question, and everything else comes after it?

- **Expand / Feedback:**
- Any other perspectives about this that different from mine which can be used as references, cite them
- So for TDD, where tests come first, which perspective would be helpful and why?

- **Validate**
I checked the cited [source](https://martinfowler.com/bliki/IntegrationTest.html) for core ideas and give it a quick read

## **Personal insight**
For me, TDD oddly reassemble a standard 3 turn dabate match:
- First speaker - Red: Define the main conflicts, targets, win conditions, stakeholders and their priorities.
- Second speaker - Green: Build team's speech case, making statements, logic, mechanics, tackling win conditions, proposing policy.
- Final speaker - Refactor: Forbid to making any new point, making back up for established logic, clarity the reasoning, clearing up misunderstands or poorly wording.