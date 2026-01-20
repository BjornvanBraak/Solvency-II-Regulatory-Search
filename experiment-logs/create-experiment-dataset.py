import os
import json
num_participants = 7
participants = [i for i in range(1, num_participants + 1)]
# column metadata: 'Language',	'Difficulty Rating'	'Label',
metadata = [
  {"conversation_id": "f0fdf43f-4856-4635-a08e-add0a0c571a0", "language": 'NL',	"difficulty": 'Easy', "label": 'Not Answerable Based On Regulation'},
  {"conversation_id": "2f08b137-3a79-4570-962b-1295c0cd1065", "language": 'NL',	"difficulty": 'Medium', "label": 'Correct'},
  {"conversation_id": "ebad075f-f33f-4ba3-b3f1-19f11c210565", "language": 'EN',	"difficulty": 'Easy', "label": 'Not Answerable Based On Regulation'},
  {"conversation_id": "dc5e1dae-0044-41b1-b8c0-458253acfc21", "language": 'NL',	"difficulty": 'Hard', "label": 'Correct'},
  {"conversation_id": "6c2a7aa8-748f-4c73-a48d-422ef00ea9aa","language": 'NL',	"difficulty": 'Easy', "label": 'Correct'},
  {"conversation_id": "e399e282-cf7b-4519-b4ac-125eb5e45c78","language": 'NL',	"difficulty": 'Easy', "label": 'Correct'},
  {"conversation_id": "376807a1-6d37-4ad1-8309-397ddc3cf74f","language": 'NL',	"difficulty": 'Easy', "label": 'Partially Correct'},
  {"conversation_id": "80d296a3-06f6-4c7e-9422-8e5c4b6f7bdc","language": 'NL',	"difficulty": 'Easy', "label": 'Partially Correct'},
  {"conversation_id": "27c756c3-87dd-44fb-afc0-6b2fc1d2c9d3","language": 'NL',	"difficulty": 'Hard', "label": 'Correct'},
  {"conversation_id": "0df0914a-ca81-4669-9d59-7b8196f38760","language": 'NL',	"difficulty": 'Medium', "label": 'Correct'},
  {"conversation_id": "750a0f34-045e-4fc3-8d59-1ce0b7e321e2","language": 'NL',	"difficulty": 'Hard', "label": 'Incorrect'},
  {"conversation_id": "4fc20992-5266-4e21-87db-89c27a5bb53e","language": 'NL',	"difficulty": 'Easy', "label": 'Correct'},
  {"conversation_id": "0481f50e-1b63-4edc-a27b-d471dd99d312","language": 'NL',	"difficulty": 'Easy', "label": 'Not Answerable Based On Regulation'},
  {"conversation_id": "32a6ae81-18c9-4604-943c-fc7255769b2b","language": 'NL',	"difficulty": 'Easy', "label": 'Correct'},
  {"conversation_id": "514f1661-ab09-460a-b042-eb3e85a3f00c","language": 'NL',	"difficulty": 'Hard', "label": 'Correct'},
  {"conversation_id": "8130d59b-4737-415a-a955-58748cea2f47","language": 'NL',	"difficulty": 'Medium', "label": 'Correct'},
  {"conversation_id": "af1d3e6b-6fc8-4e20-b4d1-c8b5f235ef67","language": 'NL',	"difficulty": 'Easy', "label": 'Correct'},
  {"conversation_id": "d351d27b-507a-4499-a427-2d85285b672e","language": 'NL',	"difficulty": 'Medium', "label": 'Correct'},
  {"conversation_id": "2e6e248c-bf19-41f2-8f8c-c8f8c4523ff8","language": 'NL',	"difficulty": 'Hard', "label": 'Not Answerable Based On Regulation'},
  {"conversation_id": "e1655614-6435-4e6f-9b0b-77bf54cb23da","language": 'NL',	"difficulty": 'Easy', "label": 'Partially Correct'},
  {"conversation_id": "52277f22-668a-47f3-955b-2eafd099237c","language": 'EN',	"difficulty": 'Medium', "label": 'Incorrect'},
  {"conversation_id": "217d9f91-f672-4d2a-a2cd-8ce6283f6834","language": 'EN',	"difficulty": 'Hard', "label": 'Correct'},
  {"conversation_id": "6c3f6958-ae65-4bd3-b983-bf2032a659be","language": 'NL',	"difficulty": 'Hard', "label": 'Correct'},
  {"conversation_id": "32596a0d-1d8f-47e2-948a-52f60ebbefaa","language": 'NL',	"difficulty": 'Medium', "label": 'Correct'},
  {"conversation_id": "b468963c-5a41-4c0f-ba78-83fe99d48f5e","language": 'NL',	"difficulty": 'Easy', "label": 'Not Answerable Based On Regulation'},
  {"conversation_id": "2ecfcdb6-f6c7-4c8c-a2a7-20fa7aa6499e","language": 'NL',	"difficulty": 'Easy', "label": 'Incorrect'},
  {"conversation_id": "94224ef1-2931-4b39-9e72-2e97838aa26c","language": 'NL',	"difficulty": 'Medium', "label": 'Correct'},
  {"conversation_id": "eb7f1a3a-5737-485c-bfd2-26eee2edfe3c","language": 'NL',	"difficulty": 'Hard', "label": 'Not Answerable Based On Regulation'},
]

with open("experiment-logs/participants.jsonl", "w") as outfile:

  total_conversations = 0
  current_conversation_idx = 0
  for participant in participants:
      conversation_file_paths = os.listdir(f"experiment-logs/participant-{participant}/backups")
      print(f"Participant {participant} has {len(conversation_file_paths)} conversations.")
      for idx, conversation_file_name in enumerate(conversation_file_paths):
        conversation_id = f"{conversation_file_name.split('backup-')[1].split('.json')[0]}"
        with open(f"experiment-logs/participant-{participant}/backups/{conversation_file_name}", "r", encoding="utf-8") as infile:
          conversation = json.load(infile)
          print(conversation_id)
          meta = next(meta for meta in metadata if meta["conversation_id"] == conversation_id)
          conversation = {
              "participant_id": participant,
              "conversation_id": conversation_id,
              "label": meta["label"],
              "language": meta["language"],
              "difficulty": meta["difficulty"],
              "conversation": [f"{turn['role']}: {turn['content']}" for turn in conversation],
              "conversation_with_metadata": conversation
          }
          outfile.write(json.dumps(conversation))
          outfile.write("\n")
          current_conversation_idx += 1

      total_conversations += len(conversation_file_paths)
  print("total conversations:", total_conversations)
  print("expected conversation idx: ", current_conversation_idx)