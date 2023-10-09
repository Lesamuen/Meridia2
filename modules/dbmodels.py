'''Contains all SQLAlchemy ORM models'''

from typing import List, Optional, Tuple, Dict
from datetime import datetime, timedelta

from sqlalchemy import ForeignKey, select, insert, update, delete
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session

from bot import SQLBase
from auxiliary import InvalidArgumentError

class User(SQLBase):
    '''
    Represents the saved data corresponding to a single discord user.

    ### Attributes
    id: str
        Corresponds to Discord user ID

    electrum: int
        Currency for this bot, per user

    beacon_touches: int
        How many times this user has touched the beacon

    dawnbreaker_progress: int
        Current progress on the quest to find the Dawnbreaker; see beacon.py for more info

    beacon_cd: datetime
        The end time for a cooldown for various beacon-related things
        
    ### Methods
    [STATIC] find_user(session: Session, id: str) -> User
        Returns the User object corresponding to the given Discord ID

    add_electrum(session: Session, electrum: int) -> None
        Adds a number of electrum pieces to user's currency

    touch_beacon(session: Session) -> None
        Increments beacons touched by 1 for this user

    dawnbreaker(session: Session, progress: int) -> None
        Sets dawnbreaker progress for this user

    set_cd(session: Session, time: timedelta) -> None
        Sets the cooldown timer for this user

    reset_cd(session: Session) -> None
        Ends the cooldown timer for this user
    '''

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key = True)
    electrum: Mapped[int] = mapped_column(default = 0)
    beacon_touches: Mapped[int] = mapped_column(default = 0)
    dawnbreaker_progess: Mapped[int] = mapped_column(default = 0)
    beacon_cd: Mapped[Optional[datetime]]

    @staticmethod
    def find_user(session: Session, id: int) -> 'User':
        '''
        Returns the User object corresponding to the given Discord ID

        ### Parameters
        session: Session
            Database session scope

        id: int
            Discord user ID

        ### Returns
        User object with matching id. Creates new user object if no match found.
        '''

        found_user = session.execute(
            select(User)
            .where(User.id == id)
            ).scalar()
        if found_user is None:
            new_user = User(id = id)
            session.add(new_user)
            session.commit()
            return new_user
        else:
            return found_user

    def add_electrum(self, session: Session, electrum: int) -> None:
        '''
        Adds a number of electrum pieces to user's currency

        ### Parameters
        session: Session
            Database session scope

        electrum: int
            Amount of electrum to add or remove (if negative) from account

        ### Throws
        InvalidArgumentError
            Electrum to remove is larger than amount of electrum available
        '''

        if -electrum > self.electrum:
            raise InvalidArgumentError
        
        self.electrum += electrum
        session.commit()

    def touch_beacon(self, session: Session) -> None:
        '''
        Increments beacons touched by 1 for this user

        ### Parameters
        session: Session
            Database session scope
        '''

        self.beacon_touches += 1
        session.commit()

    def dawnbreaker(self, session: Session, progress: int) -> None:
        '''
        Sets dawnbreaker progress for this user; -1 through 20

        ### Parameters
        session: Session
            Database session scope

        progress: int
            The number to set progress to

        ### Throws
        InvalidArgumentError
            Provided number is not in range -1 to 20
        '''

        if progress < -1 or progress > 20:
            raise InvalidArgumentError

        self.dawnbreaker_progess = progress
        session.commit()

    def set_cd(self, session: Session, time: timedelta) -> None:
        '''
        Sets the cooldown timer for this user

        ### Parameters
        session: Session
            Database session scope

        time: timedelta
            How long after current time until cooldown is over
        '''

        self.beacon_cd = datetime.utcnow() + time
        session.commit()

    def reset_cd(self, session: Session) -> None:
        '''
        Ends the cooldown timer for this user

        ### Parameters
        session: Session
            Database session scope
        '''

        self.beacon_cd = None
        session.commit()