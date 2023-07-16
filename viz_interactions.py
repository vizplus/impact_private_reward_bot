from viz import Client
from viz.account import Account
from vizbase.account import PrivateKey

node = 'wss://node.viz.cx/ws'


def check_viz_account(account_name: str) -> bool:
    '''
    Provide a VIZ account name. Returns True if there is such an account,
    otherwise returns False.

    :param str account_name: Name of the account
    '''
    try:
        Account(
            account_name=account_name, blockchain_instance=Client(node=node)
        )
        return True
    except Exception:
        return False


def check_viz_account_capital(account_name: str) -> bool:
    '''
    Provide a VIZ account name.
    Returns True if account capital is >= 25000 viz, otherwise returns False.

    :param str account_name: Name of the account
    '''
    acc = Account(
            account_name=account_name, blockchain_instance=Client(node=node)
        )
    acc_vs = float(acc['vesting_shares'].split()[0])
    acc_rvs = float(acc['received_vesting_shares'].split()[0])
    acc_dvs = float(acc['delegated_vesting_shares'].split()[0])
    acc_capital = acc_vs + acc_rvs - acc_dvs
    if acc_capital >= 1:
        return True
    else:
        return False


def check_reg_key_correct(regular_key: str, account_name: str) -> bool:
    '''
    Provide a regular_key and the corresponding VIZ account name.
    Returns True if there is such a regular_key in blockchain.

    :param str regular_key: Private regular key
    :param str account_name: Name of the account
    '''
    try:
        public = PrivateKey(
            regular_key, prefix='VIZ'
        )
        acc = Account(
                account_name=account_name,
                blockchain_instance=Client(node=node)
            )
        items = dict(acc.items())
        str_pubkey = str(public.pubkey)
        public_reg_key = items['regular_authority']['key_auths'][0][0]
        return str_pubkey == public_reg_key
    except Exception:
        return False
