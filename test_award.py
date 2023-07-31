from viz import Client
from viz.account import Account
from vizbase.account import PrivateKey
from viz.memo import Memo
from pprint import pprint

node = 'wss://node.viz.cx/ws'
client = Client(node=node)
# viz.lexai.host

def count_vip_energy_to_spend(account_name: str, reward_size: float) -> float:
    '''
    Provide a VIZ account name and the reward size.
    Returns an energy to spend.

    :param str account_name: Name of the account
    :param float reward_size: Reward size of the account
    '''
    try:
        #  get award-on-capital data required for the calculations
        award_on_capital_acc = Account(
                account_name='award-on-capital',
                blockchain_instance=client
            )
        history = list(award_on_capital_acc.get_account_history(-1, 1))[0]
        json = history['json']
        award_on_capital = json.split(',')[-1].strip()[:-2]
        award_on_capital_value = float(award_on_capital.split()[1].strip())
    except Exception:
        print('Couldn\'t connect to service that calculates award-on-capital')

    try:
        # get vip-user data required for the calculations
        vip_acc = Account(
                account_name=account_name,
                blockchain_instance=client
            )
        energy = vip_acc['energy']
        vs = float(vip_acc['vesting_shares'].split()[0])
        rvs = float(vip_acc['received_vesting_shares'].split()[0])
        dvs = float(vip_acc['delegated_vesting_shares'].split()[0])
        effective_capital = vs + rvs - dvs
    except Exception:
        print('Couldn\'t connect to service that calculates needed used data')

    # calculations
    available_capital = (award_on_capital_value * effective_capital *
                         (energy / 10000))
    result = (energy / 100) / available_capital * reward_size
    return round(result, 2)


def reward_user(
        account: str,
        reward_size: float,
        forwarded_message: str,
        author_id: str,
        # regular_key: str,
        # memo_key: str = ''
) -> None:
    '''
    Provide a VIZ account name, reward size, memo and a receiver.
    Transfers assets to tg.viz user.

    :param str account_name: Name of the account
    :param float reward_size: Reward size of the account
    :param str key: Initiator regular key
    :param str memo: The message following the transaction
    '''
    # receiver_pub_memo_key = 'VIZ61KuXnrWbTqxzHC82p8nQLUSPZpYudr5412r4rG6ruibBSKnDS'
    client = Client(
        node=node, keys=[
            '5JWY8Ww6eFYsZHRJTzCQ8WCT4vrfXoQS5epkkPvgqAqUYREG9Lw',
            '5Jet4kTUoQWBvpQt8gKQHkjbVyWzC6xEXoVnRxqWSGoT8AXZcnN',

        ]
    )

    energy = count_vip_energy_to_spend(account, reward_size)
    memo = f'{account};;{author_id};;{forwarded_message}'
    m = Memo('roklem', 'first.roklem', blockchain_instance=client)
    m.unlock_wallet('secret')
    # m
    encrypted_memo = (m.encrypt(memo))

    client.award(
        receiver='first.roklem',
        energy=energy,
        account=account,
        memo=encrypted_memo
    )
    print('award successful')


print(reward_user(
    'first.roklem',
    1,
    'my name is not for sounding',
    '23929392',
    # '5Jet4kTUoQWBvpQt8gKQHkjbVyWzC6xEXoVnRxqWSGoT8AXZcnN',
    # 'VIZ7HngCXC9Tp4nwJNEKjBuEw6uCVB3e4mcrtWyH6qW7J2J6UCpAw'
))

# client = Client(
#         node=node, keys=[
#             '5JWY8Ww6eFYsZHRJTzCQ8WCT4vrfXoQS5epkkPvgqAqUYREG9Lw',
#             '5Jet4kTUoQWBvpQt8gKQHkjbVyWzC6xEXoVnRxqWSGoT8AXZcnN',
#             '5KdKVEKEsriCKjTSt4p7Hs8N5YmCUCE6bJ2bVRq8JhYwAmfoTty',
#             '5JkPRV4QF5EiK77nPiUxwCmaezEEXufwipfJT2JiamXxt87uwn7'
#         ]
#     )
# m = Memo("roklem", "bob", blockchain_instance=client)
# m.unlock_wallet("secret")
# enc = (m.encrypt("roklem;;1510322344;;'Отличный проект - мы покупатели их сервиса!'"))
# print(enc)
# print(m.decrypt(enc))

# memo public roklem VIZ7eByLDgvyYezLDPf2X758SfPbtbpooCcnVBgSL48XqRG3s6y7h
# roklem = Account('roklem', client)
# print(dict(roklem.items())['memo_key'])