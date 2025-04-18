# Pinterest Customer Support Engine
A webapp that uses retrieval-augmented generation (RAG) in conjunction with a knowledge graph (KG) to answer customer questions.

## Knowledge Domain & Schema Design
**Domain:** Content sharing on Pinterest, a social media platform that allows users to discover, save, and share visual content. A customer can use this application to learn how their pins and boards are shared with other Pinterest users.

Below is a breakdown of the KG schema design.

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
