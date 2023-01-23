# Contributing

## Caveat

This is a quick-and-dirty prototype; speed of implementation was chosen over best practices and proper frameworks. Some of the required improvements are tracked via the GH issues for each project; many are still in the author's head, waiting to get documented in their spare time :-)

In particular, the orchestration should at least be done via docker-compose, the server should be implemented at least as flask (widely understood and supported), and the frontend should not be vanilla JS (no matter how exciting that is).

## Brief overview of files and functionality

### Orchestration
[./setup.sh](./setup.sh) ; see also the section (#Orchestration)[#Orchestration].
* prepares environment
* launches server
* sets up visual verification

### Backend
[./server.py](./server.py)
* the actual server code, written using [lib/http/server](https://docs.python.org/3/library/http.server.html)
* POST: accepts json, passes to model-generation code
* GET:  returns scored json, retreieved from model-generation code


### Frontend
For a visual overview, see the `User Interface` section ["User Interface" section in the system design documentation.](https://github.com/YoinkBird/cyclesafe/blob/613f6dcc4a95d4394546f2ba83d20263461a02b4/docs/report/report.md#user-application).

[./directions.html](./directions.html)
* rudimentary webpage using Vanilla JS to implement google maps API
* displays scored routes based on model predictions
* sends direction json to server
* receives scored json from server
* displays original directions with score as mapmarker
* **Caveat**: currently non-functional due to outdated Google Maps API Key; easy to fix, but it doesn't block testing while modernising the rest of the application so it's a low priority.
* **Caveat**: chock full of [JavaScript sins](https://github.com/YoinkBird/cyclesafe_server/blob/60c8ffaea646c9f680458f03c5ddef7f055a65df/client.html#L106), but good enough for a rapid prototype.

## Orchestration

**Caveat**: Orchestration is done in a pure Linux fashion, and does not use any modern encapsulation techniques (i.e. no VM, Container, etc). Fixing this is an active WIP.

**Process Lifecycle**

The script manually manages the server lifecycle by [tracking PIDs](https://github.com/YoinkBird/cyclesafe_server/blob/042205c4797c1c8450879f8659ad4384589811ef/setup.sh#L171) and then [reaping them for shutdown](https://github.com/YoinkBird/cyclesafe_server/blob/042205c4797c1c8450879f8659ad4384589811ef/setup.sh#L222)
 and [closing sockets](https://github.com/YoinkBird/cyclesafe_server/blob/042205c4797c1c8450879f8659ad4384589811ef/setup.sh#L180).

Edge cases: Sometimes, [manual steps](https://github.com/YoinkBird/cyclesafe_server/blob/042205c4797c1c8450879f8659ad4384589811ef/setup.sh#L121) are still required to avoid missing any edge cases which containerized solutions already manage.

**Dependency Management**

The [model management backend is downloaded from a separate repository](https://github.com/YoinkBird/cyclesafe_server/blob/042205c4797c1c8450879f8659ad4384589811ef/setup.sh#L89).

The [file generation preparation](https://github.com/YoinkBird/cyclesafe_server/blob/042205c4797c1c8450879f8659ad4384589811ef/setup.sh#L130) relies on manipulating files on local disk; this was a quick hack to keep the server code decoupled from the model management code.

The [file generation cleanup](https://github.com/YoinkBird/cyclesafe_server/blob/042205c4797c1c8450879f8659ad4384589811ef/setup.sh#L100) ensures that old files are not used by mistake; this is perfect for a Jenkins-based CI/CD but is not long for this world.

### Testing

Verification is implemented as an [interface test](https://github.com/YoinkBird/cyclesafe_server/blob/042205c4797c1c8450879f8659ad4384589811ef/setup.sh#L187); this is implemented using `curl` and json files defining requests and expected responses (similar to [expect testing](https://en.wikipedia.org/wiki/Expect); this is a quick and dirty way to verify system functionality at a high level; see rationale at the end of this section.

UI Testing is done manually by [launching a web browser](https://github.com/YoinkBird/cyclesafe_server/blob/042205c4797c1c8450879f8659ad4384589811ef/setup.sh#L212) and manually manipulating the fields; due to prototyping time constraints this was not automated, but could be using cypress or selenium.

Rationale: During development, the trade-off was made to rely on integration testing to prevent backsliding, with unit tests to be added later where possible. This is both due to the nature of testing ML models (results aren't always predictable) and the prototype nature of the project (i.e. most of the code is expected to be refactored anyway).

## Related Projects

Original server code adopted from https://gist.github.com/nitaku/10d0662536f37a087e1b
, because the server needed only to be a shim around the model to quickly get a working prototype, and for the minimal routes required it was deemed faster to use vanilla HTTP instead of learning a new framework.
