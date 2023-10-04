from sqlalchemy import ForeignKey, select, insert, update, delete
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from typing import List, Optional, Tuple, Dict

from bot import SQLBase

class User(SQLBase):
    '''
    Represents the saved data corresponding to a single discord user.

    ### Attributes
    id: str
        Corresponds to Discord user ID

    beacon_touches: int
        How many times this user has touched the beacon

    dawnbreaker: bool
        Whether this user has pulled the dawnbreaker yet or not
        
    ### Methods
    [STATIC] find_user(session: Session, id: str) -> User
        Returns the User object corresponding to the given Discord ID

    touch_beacon(session: Session) -> None
        Increments beacons touched by 1 for this user

    dawnbreaker(session: Session) -> None
        Sets dawnbreaker flag
    '''

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key = True)
    beacon_touches: Mapped[int] = mapped_column(default = 0)
    dawnbreaker: Mapped[bool] = mapped_column(default = False)

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

    def touch_beacon(self, session: Session) -> None:
        '''
        Increments beacons touched by 1 for this user

        ### Parameters
        session: Session
            Database session scope
        '''

        self.beacon_touches += 1
        session.commit()