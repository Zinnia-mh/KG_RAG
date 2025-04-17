# Pinterest Customer Support Engine
A webapp that uses retrieval-augmented generation (RAG) in conjunction with a knowledge graph (KG) to answer customer questions.

## Knowledge Domain & Schema Design
**Domain:** Status of shared pins and boards on Pinterest, a social media platform that allows users to discover, save, and share visual content. Below is a breakdown of the KG schema design.

### Entities
- **User**: Individuals with Pinterest accounts
    - **Properties:** user_id, username, is_current_user
- **Pin**: Posts uploaded to Pinterest by users
    - **Properties:** pin_id, url
- **Board**: Collections of pins created by users
    - **Properties:** board_id, is_private
- **ShareEvent**: Instances when users share pins/boards with each other
    - **Properties:** share_id, content_type, timestamp
- **Group**: Collections of users who can view a board
    - **Properties:** group_id, permissions

### Relationships
- **Core**
    - User -[CREATES]-> (Pin | Board)
    - User -[FOLLOWS]-> (User | Board)
    - User -[BLOCKS]-> User
    - User -[SAVES]-> Pin
    - Board -[CONTAINS]-> Pin
- **Sharing**
    - User -[SHARES]-> ShareEvent
    - ShareEvent -[CONTENT]-> (Pin | Board)
    - ShareEvent -[RECEIVER]-> User
- Groups
    - Group -[ACCESSES]-> Board
    - User -[JOINS]-> Group
