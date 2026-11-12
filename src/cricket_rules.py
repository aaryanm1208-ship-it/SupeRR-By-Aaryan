"""
Cricket rules and scoring engine for SupeRR Selector Season 2.
Implements Marylebone Cricket Club (MCC) Laws of Cricket and ICC T20 Playing Conditions.
"""

import pandas as pd
import numpy as np
from src import config


def is_legal_delivery_series(extras_type_series: pd.Series) -> pd.Series:
    """
    Returns boolean series indicating whether each delivery is a legal delivery.
    Illegal deliveries: wide, Overstep (no-ball), other (no-ball), Penalty.
    Legal deliveries: unassisted deliveries, legbyes, byes.
    """
    return ~extras_type_series.isin(config.ILLEGAL_EXTRAS | {"Penalty"})


def is_ball_faced_series(extras_type_series: pd.Series) -> pd.Series:
    """
    Returns boolean series indicating whether delivery counts as a ball faced by the batter.
    Wides and penalty awards do NOT count as balls faced.
    Legal deliveries and no-balls (Overstep, other) DO count as balls faced.
    """
    return ~extras_type_series.isin({"wide", "Penalty"})


def get_bowler_charged_runs_series(
    runs_series: pd.Series,
    extras_type_series: pd.Series,
    extras1_runs_series: pd.Series
) -> pd.Series:
    """
    Calculates runs charged to the bowler for each delivery.
    Bowler is charged for:
    - Runs scored off the bat (runs)
    - Wide extras (extras1_runs when extras_type == 'wide')
    - No-ball extras (extras1_runs when extras_type in ['Overstep', 'other'])
    Bowler is NOT charged for:
    - Byes
    - Leg-byes
    - Penalty runs
    - Secondary extras (extras_2_runs, representing byes/leg-byes occurring on a no-ball)
    """
    bowler_extras = extras1_runs_series.where(extras_type_series.isin(config.BOWLER_CHARGED_EXTRAS), 0)
    return runs_series + bowler_extras


def is_bowler_wicket_series(is_wicket_series: pd.Series, dismissal_type_series: pd.Series) -> pd.Series:
    """
    Returns boolean series indicating whether dismissal is credited to the bowler.
    Bowler-credited: Bowled, Caught, LBW, Stump, Hit Wicket.
    Non-bowler: RunOut, Retire Out, Obstructing the field.
    """
    return is_wicket_series & dismissal_type_series.isin(config.BOWLER_CREDITED_DISMISSALS)


def is_non_bowler_dismissal_series(is_wicket_series: pd.Series, dismissal_type_series: pd.Series) -> pd.Series:
    """
    Returns boolean series indicating whether dismissal is a non-bowler-credited wicket (e.g. RunOut).
    """
    return is_wicket_series & dismissal_type_series.isin(config.NON_BOWLER_DISMISSALS)


def get_innings_stage(overid: int) -> str:
    """Classifies over into innings stage: Powerplay, Middle, Death."""
    if overid <= 6:
        return config.STAGE_POWERPLAY
    elif overid <= 15:
        return config.STAGE_MIDDLE
    else:
        return config.STAGE_DEATH


def get_innings_stage_series(overid_series: pd.Series) -> pd.Series:
    """Vectorized classification of over into innings stage."""
    return pd.Series(
        np.select(
            [overid_series <= 6, overid_series <= 15],
            [config.STAGE_POWERPLAY, config.STAGE_MIDDLE],
            default=config.STAGE_DEATH
        ),
        index=overid_series.index
    )
