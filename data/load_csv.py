#
# load_csv.py
#   Author: Bill Xia
#   Created: 4/17/25
#
# Purpose: Loads data from a CSV file into a Neo4j knowledge graph.
#
#    Note: This file is no longer necessary; Neo4j's browser interface lets
#          us directly upload and associate data.
#

# Imports.
from json import load
from neo4j import GraphDatabase

# Functions. - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def gds_client():
    '''
    Function that loads and returns the GDS client.
    '''
    # Swap this with fp to your API key.
    with open('../../../Documents/API_Keys/Neo4j-Instance01.json') as fp:
        credentials = load(fp)

    # Replace with the actual URI, username, and password
    AURA_CONNECTION_URI = credentials['NEO4J_URI']
    AURA_USERNAME       = credentials["NEO4J_USERNAME"]
    AURA_PASSWORD       = credentials["NEO4J_PASSWORD"]

    return GraphDatabase.driver(
        AURA_CONNECTION_URI,
        auth=(AURA_USERNAME, AURA_PASSWORD)
    )

def enforce_constraints(client):
    '''
    Function that enforces constraints. For our program, that means enforceing
    uniqueness.
    '''
    pairs = [
        ('user:User',        'user.username'),
        ('pin:Pin',          'pin.pin_id'),
        ('board:Board',      'board.board_id'),
        ('group:Group',      'group.group_id'),
        ('share:ShareEvent', 'share.share_id')
    ]
    with client.session() as session:
        for p in pairs:
            curr_query = f"""
                CREATE CONSTRAINT FOR ({p[0]}) REQUIRE {p[1]} IS UNIQUE
            """
            session.run(curr_query).data()

    return client

def load_csvs(client, debug=False):
    '''
    Function that loads CSV data into GDS format.
    '''
    # Load entities.
    triples = [
        ["'users.csv'", 
         "(u:User {username: row.username})",
         "u.is_private = row.private"],
        ["'pins.csv'",
         "(p:Pin {pin_id: row.pin_id})",
         "p.caption = row.caption, p.url = row.url"],
        ["'boards.csv'",
         "(b:Board {board_id: row.board_id})",
         "b.name = row.board_name, b.is_private = row.private"],
        ["'shares.csv'",
         "(s:ShareEvent {share_id: row.share_id})",
         "s.share_time = row.share_time"],
        ["'groups.csv'",
         "(g:Group {group_id: row.group_id})",
         "g.permissions = row.permissions"]
    ]
    with client.session() as session:
        for t in triples:
            ret = session.run(f"""
                LOAD CSV WITH HEADERS
                FROM {t[0]} AS row
                MERGE {t[1]}
                ON CREATE SET {t[2]}
                RETURN count(*)
            """).data()
            if debug:
                print(f"Size of {t[0]} : {ret}")

# Main. - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def main():
    gds = gds_client()
    gds = enforce_constraints(gds)
    # gds = load_csvs(gds, debug=True)

if __name__ == '__main__':
    main()