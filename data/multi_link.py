#
# multi_link.py
#   Author: Bill Xia
#   Created: 4/17/25
#
# Purpose: Links boards and pins, as well as users and their followers into
#          two new csv files.
#
import csv

def process_boards(input_file, output_file):
    with open(input_file, newline='') as boards_csv, open(output_file, 'w', newline='') as out_csv:
        reader = csv.DictReader(boards_csv)
        writer = csv.DictWriter(out_csv, fieldnames=["board_id", "pin_id"])
        writer.writeheader()

        for row in reader:
            board_id = row["board_id"]
            pins     = row["pins"]
            if pins:
                for pin_id in pins.split(";"):
                    writer.writerow({"board_id": board_id, "pin_id": pin_id.strip()})


def process_users(input_file, output_file):
    with open(input_file, newline='') as users_csv, open(output_file, 'w', newline='') as out_csv:
        reader = csv.DictReader(users_csv)
        writer = csv.DictWriter(out_csv, fieldnames=["from_user", "to_user", "relationship"])
        writer.writeheader()

        for row in reader:
            from_user = row["username"]

            following = row.get("following", "")
            if following:
                for to_user in following.split(";"):
                    to_user = to_user.strip()
                    if to_user:
                        writer.writerow({"from_user": from_user, "to_user": to_user, "relationship": "FOLLOWS"})

            blocked = row.get("blocked", "")
            if blocked:
                for to_user in blocked.split(";"):
                    to_user = to_user.strip()
                    if to_user:
                        writer.writerow({"from_user": from_user, "to_user": to_user, "relationship": "BLOCKS"})

def main():
    process_boards("boards.csv", "board_contains_pin.csv")
    process_users("users.csv", "user_relationships.csv")

if __name__ == '__main__':
    main()