# Pinterest Customer Support Engine
A webapp that uses retrieval-augmented generation (RAG) in conjunction with a knowledge graph (KG) to answer customer questions.

I developed this app to strengthen my understanding of knowledge bases and RAG.

## Knowledge Domain & Schema Design
**Domain:** Content sharing on Pinterest, a social media platform that allows users to discover, save, and share visual content. A customer can use this application to learn how their pins and boards are shared with other Pinterest users.

Below is a breakdown of the KG schema design, which I implmented on Neo4j. I populated the graph with made-up data (since I don't have access to Pinterest's user data), which can be found in `data/`.

### Entities
- **User**: Individuals with Pinterest accounts
    - **Properties:** username (unique), is_private
- **Pin**: Posts uploaded to Pinterest by users
    - **Properties:** pin_id (unique), caption, url
- **Board**: Collections of pins created by users
    - **Properties:** board_id (unique), board_name, is_private
- **ShareEvent**: Instances when users share pins/boards with each other
    - **Properties:** share_id (unique), content_type, timestamp
- **Group**: Collections of users who can view a board
    - **Properties:** group_id (unique), permissions

### Relationships
- **Core**
    - User -[CREATED]-> (Pin | Board | Group)
    - User -[FOLLOWS]-> (User | Board)
    - User -[BLOCKS]-> User
    - User -[SAVES]-> Pin
    - Board -[CONTAINS]-> Pin
- **Sharing**
    - User -[SHARES]-> ShareEvent
    - ShareEvent -[DELIVERS]-> (Pin | Board)
    - ShareEvent -[HAS_RECIPIENT]-> User
- Groups
    - Group -[CAN_ACCESSE]-> Board
    - Group -[HAS_MEMBER]-> User

## Usage
**Step 1.** Activate the virtual environment by `cd`-ing into this directory, then running the following command in terminal: `source KGRAG_env/bin/activate`.

**Step 2.** Start up the backend by running `python3 pinterest_kgrag/backend/app.py` in terminal from the same directory.

**Step 3.** Start up the frontend by running `npm start` in terminal from the same directory. The program will automatically open in your preferred browser.

## Limitations and Next Steps
Because the focus of this project was the creation of a knowledge graph and RAG system, I did not spend as much time on **model accuracy** or **security**. Should I return to this project in the future, I would address limitations in both those domains. Below are some ideas for how I would do so.

### Model Accuracy
A challenge for smaller LLMs (which I was constrained to by my local hardware) is generating accurate code in less main-stream languages such as Cypher, the langauge used by Neo4j's knowledge graphs. A potential solution for overcoming this limitation with limited resources would be fine-tuning an LLM for this task.

To source data for fine-tuning, I would have the LLM generate Cypher queries in response to a wide variety of potential uesr queries and select the best responses among them. Normally, I don't advocate for generating training data, but for this use case, where the generated data can easily be vetted, I believe that the usual risks would mostly be mitigated.

### Security
In its current state, the app allows all users to query any information from the knowledge graph, even information that they should not have access to (e.g. sharing statistics of private users). To avoid information leaks, I would improve upon this system by blocking queries that expose information that the querier should not be able to access.