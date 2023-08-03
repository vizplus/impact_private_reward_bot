# from viz import Client
# from viz.account import Account
# from vizbase.account import PrivateKey
# from viz.memo import Memo
# from pprint import pprint

# node = 'wss://node.viz.cx/ws'
# client = Client(node=node)
# # viz.lexai.host


# client = Client(
#         node=node
#     )

# memo = 'Test message'
# m = Memo()
# encrypted_memo = (m.encrypt(memo))

# client.award(
#     receiver='first.roklem',
#     energy=1,
#     account='second.roklem',
#     memo=encrypted_memo
# )
# print('success')


from vizbase import memo
from viz.memo

# Initialize Viz instance
viz = Viz()

# Set the sender's private key
sender_private_key = "5HvPDD4X6ADEQdCmAnwNkRyfUHztxsH8u8owEHv88Z2LpeWqouZ"

# Set the recipient's account name
recipient_account = "second.roklem"

# Set the memo message you want to encrypt
memo_message = "YOUR_MEMO_MESSAGE"

# Encrypt the memo message
encrypted_memo = memo.encode_memo(sender_private_key, recipient_account, memo_message)

# Send the award using the award method
viz.award(sender_private_key, recipient_account, encrypted_memo)
