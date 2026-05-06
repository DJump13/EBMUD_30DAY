import numpy as np
import pandas as pd


def storage_change(df):
    if 'Reservoir Volume' not in df:
        raise ValueError("storage_change requires 'Reservoir Volume'")
    df['Storage Change'] = df['Reservoir Volume'] - df['Reservoir Volume'].shift(1)
    return df


def storage_gain(df):
    if 'Storage Change' not in df:
        raise ValueError("storage_gain requires 'Storage Change'")
    df['Storage Gain'] = np.where(df['Storage Change'] > 0, df['Storage Change'], 0)
    return df


def moving_max_from_start_date(df, start_date=None):
    df['Moving Max from Start Date'] = df['Reservoir Volume'].cummax()

    if start_date is None:
        return df

    start_date = pd.Timestamp(start_date)
    date_values = pd.to_datetime(df['Date'])
    reset_mask = date_values >= start_date

    if reset_mask.any():
        df.loc[reset_mask, 'Moving Max from Start Date'] = df.loc[reset_mask, 'Reservoir Volume'].cummax()

    return df


def initial_collection_to_storage(df):
    df['Initial Collection to Storage'] = \
        np.maximum(0, (df['Moving Max from Start Date'] - df['Moving Max from Start Date'].shift(1)))
    return df


def forward_30_day_moving_minimum(df):
    df['Forward 30-day Moving Minimum'] = df['Reservoir Volume'][::-1].rolling(window=30).min()[::-1]
    return df


def positive_delta_s(df):
    df['Positive Delta S'] = \
        np.maximum(0, df['Forward 30-day Moving Minimum'] - df['Forward 30-day Moving Minimum'].shift(1))
    return df


def refill_collection(df):
    df['Refill Collection'] = \
        np.minimum(df['Positive Delta S'], df['Storage Gain'] - df['Initial Collection to Storage'])
    return df


def total_collection_to_storage(df):
    df['Total Collection to Storage'] = df['Initial Collection to Storage'] + df['Refill Collection']
    return df


def regulatory_collection_to_storage(df):
    df['Regulatory Collection to Storage'] = df['Storage Gain'] - df['Total Collection to Storage']
    return df


def storage_loss(df):
    df['Storage Loss'] = np.where(df['Storage Change'] < 0, df['Storage Change'], 0)
    return df


def compute_step(i, n , q, o_prev, p_prev, s_prev, t_prev):
    # --- O: Cumulative Initial Collection ---
    o = max(0, 0 if ((i == 0) & (n > 0)) else (o_prev + i + s_prev))

    # --- P: Remaining Cumulative Reg Collection ---
    p = max(0, p_prev + n + t_prev)

    # --- R: WD ---
    r = min(0, q + p_prev + t_prev)

    # --- S: WD From Storage ---
    s = max(q, (max(-o, q) if (o > 0) else r))

    # --- T: Regulatory WD ---
    t = q - s

    return o, p, r, s, t


def the_rest(df):
    length = len(df)

    i_arr = df['Initial Collection to Storage'].values
    n_arr = df['Regulatory Collection to Storage'].values
    q_arr = df['Storage Loss'].values

    # initialize circularly-dependent columns
    o_arr = np.zeros(length)
    p_arr = np.zeros(length)
    r_arr = np.zeros(length)
    s_arr = np.zeros(length)
    t_arr = np.zeros(length)

    for index in range(length):
        if index == 0:
            o_prev = p_prev = s_prev = t_prev = 0
        else:
            o_prev = o_arr[index - 1]
            p_prev = p_arr[index - 1]
            s_prev = s_arr[index - 1]
            t_prev = t_arr[index - 1]

        i = i_arr[index]
        n = n_arr[index]
        q = q_arr[index]

        o, p, r, s, t = compute_step(i, n, q, o_prev, p_prev, s_prev, t_prev)

        # store results
        o_arr[index] = o
        p_arr[index] = p
        r_arr[index] = r
        s_arr[index] = s
        t_arr[index] = t

    df['Cumulative Initial Collection Between Reg Collections'] = o_arr
    df['Remaining Cumulative Reg Collection'] = p_arr
    df['WD'] = r_arr
    df['WD from Storage'] = s_arr
    df['Regulatory WD'] = t_arr

    return df


def category(df):
    df = df.copy()
    df.loc[:, 'Category'] = np.select(
        [
            df['Initial Collection to Storage'] != 0,
            df['Refill Collection'] > 0,
            df['Regulatory Collection to Storage'] > 0,
            df['Regulatory WD'] != 0,
            df['WD from Storage'] != 0
        ],
        ['initial', 'refill', 'reg_collection', 'reg_wd', 'wd'],
        default=None
    )

    df.loc[:, 'Category'] = df['Category'].ffill()

    return df
