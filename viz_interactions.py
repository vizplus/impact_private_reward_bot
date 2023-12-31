from viz import Client
from viz.account import Account
from vizbase.account import PrivateKey

node = 'wss://node.viz.cx/ws'
client = Client(node=node)


def check_viz_account(account_name: str) -> bool:
    '''
    Provide a VIZ account name

    :param str account_name: Name of the account

    Returns:
    - True if there is such an account,
    otherwise returns False.
    '''
    try:
        Account(
            account_name=account_name, blockchain_instance=client
        )
        return True
    except Exception:
        return False


def check_viz_account_capital(account_name: str) -> bool:
    '''
    Provide a VIZ account name

    :param str account_name: Name of the account

    Returns:
    - True if account capital is >= 25000 viz, otherwise returns False

    Raises:
    - Exception: If there is an error connecting to the service
    that checks the account capital
    '''
    try:
        acc = Account(
                account_name=account_name,
                blockchain_instance=client
            )
        acc_vs = float(acc['vesting_shares'].split()[0])
        acc_rvs = float(acc['received_vesting_shares'].split()[0])
        acc_dvs = float(acc['delegated_vesting_shares'].split()[0])
        acc_capital = acc_vs + acc_rvs - acc_dvs
        if acc_capital >= 0:
            return True
        else:
            return False
    except Exception as e:
        print(f'An error occured while checking account capital: {str(e)}')
        return False


def check_reg_key_correct(regular_key: str, account_name: str) -> bool:
    '''
    Provide a regular_key and the corresponding VIZ account name

    :param str regular_key: Private regular key
    :param str account_name: Name of the account

    Returns:
    - bool: True if the regular key matches the regular authority
    key of the account, False otherwise

    Raises:
    - Exception: If there is an error during the key comparison
    '''
    try:
        public = PrivateKey(
            regular_key, prefix='VIZ'
        )
        acc = Account(
                account_name=account_name,
                blockchain_instance=client
            )
        items = dict(acc.items())
        str_pubkey = str(public.pubkey)
        public_reg_key = items['regular_authority']['key_auths'][0][0]
        return str_pubkey == public_reg_key
    except Exception:
        return False


def count_vip_energy_to_spend(account_name: str, reward_size: float) -> float:
    '''
    Provide a VIZ account name and the reward size

    :param str account_name: Name of the account
    :param float reward_size: Reward size of the account

    Returns:
    - float: The calculated amount of energy to spend

    Raises:
    - Exception: If there is an error connecting to the service
    that calculates award-on-capital or retrieving VIP user data
    '''
    try:
        # get award-on-capital data required for the calculations
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


def count_vip_award_balance(account_name: str, reward_size: float) -> int:
    '''
    Provide a VIZ account name.
    Returns an integer number signaling the amount of awards VIZ user can do.

    :param str account_name: The name of the account
    for which to calculate the award balance
    :param float reward_size: Reward size of the account

     Returns:
    - int: The calculated award balance

    Raises:
    - Exception: If there is an error connecting to the service
    that calculates award-on-capital
    '''
    try:
        # get award-on-capital data required for the calculations
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

    # calculations
    award_balance = int((award_on_capital_value * (effective_capital)
                         * (energy / 10000)) // reward_size)

    return award_balance


########################################################################
def reward_user(
        account: str,
        reward_size: float,
        author_id: str,
        regular_key: str,
        community_id: str
) -> None:
    '''
    Transfers assets to tg.viz user, which then award the owner of
    the forwarded message

    :param str account_name: Name of the account
    :param float reward_size: Reward size of the account
    :param str author_id: the forwarded message author ID
    :param str regular_key: Initiator regular key
    :param str community_id: The community ID
    '''
    client = Client(
        node=node, keys=[regular_key]
    )

    energy = count_vip_energy_to_spend(account, reward_size)
    memo = f'{account};;{author_id};;{community_id}'

    client.award(
        receiver='tg.viz',  # tg.viz must be the reciever of the award
        energy=energy,
        account=account,
        memo=memo
    )
    print('award successful')
#
