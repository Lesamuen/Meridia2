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
    [PRIMARY] id: str
        Corresponds to Discord user ID

    electrum: int
        Currency for this bot, per user

    beacon_touches: int
        How many times this user has touched the beacon

    dawnbreaker_progress: int
        Current progress on the quest to find the Dawnbreaker; see beacon.py for more info

    beacon_cd: datetime
        The end time for a cooldown for various beacon-related things

    [BACKREF] char_inv: List[CollectedCharacter]
        List of characters this User owns
        
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
    '''Corresponds to Discord user ID'''
    electrum: Mapped[int] = mapped_column(default = 0)
    '''Currency for this bot, per user'''

    beacon_touches: Mapped[int] = mapped_column(default = 0)
    '''How many times this user has touched the beacon'''
    dawnbreaker_progess: Mapped[int] = mapped_column(default = 0)
    '''Current progress on the quest to find the Dawnbreaker; see beacon.py for more info'''
    beacon_cd: Mapped[Optional[datetime]]
    '''The end time for a cooldown for various beacon-related things'''

    char_inv: Mapped[List["CollectedCharacter"]] = relationship(back_populates = "owner", cascade = "all, delete-orphan", passive_deletes = True)
    '''List of characters this User owns'''

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
            # Create new default user data if no matching user data found
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


class CollectedCharacter(SQLBase):
    '''
    Represents a single collected character in a User's inventory 
    
    ### Attributes
    [PRIMARY, FOREIGN] owner_id: int
        ID of User who owns this character

    [BACKREF] owner: User
        Direct reference to User who owns this character

    [PRIMARY] char_id: int
        ID of the character owned

    obtained: datetime
        Time that this character was first obtained, disregarding duplicates

    banner_id: int
        ID of the banner this character was first obtained from

    dupes: int
        How many duplicates of this character the User owns

    ### Methods
    [STATIC] find(session: Session, user_id: int, char_id: int) -> CollectedCharacter | None
        Find the CollectedCharacter instance that corresponds to this user and character, if it exists
    
    [STATIC] obtain(session: Session, user_id: int, char_id: int, banner_id: int) -> None
        Create a new CollectedCharacter instance

    gain(session: Session) -> None
        Adds 1 duplicate to this character

    sell(session: Session, amount: int) -> None
        Removes a number of duplicates from this character
    '''

    __tablename__ = "collected_char"

    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete = "CASCADE"), primary_key = True)
    '''ID of User who owns this character'''
    owner: Mapped["User"] = relationship(back_populates = "char_inv")
    '''Direct reference to User who owns this character'''
    char_id: Mapped[int] = mapped_column(primary_key = True)
    '''ID of the character owned'''
    obtained: Mapped[datetime]
    '''Time that this character was first obtained, disregarding duplicates'''
    banner_id: Mapped[int]
    '''ID of the banner this character was first obtained from'''
    dupes: Mapped[int] = mapped_column(default = 1)
    '''How many duplicates of this character the User owns'''

    @staticmethod
    def find(session: Session, user_id: int, char_id: int) -> "CollectedCharacter" | None:
        '''
        Find the CollectedCharacter instance that corresponds to this user and character, if it exists

        ### Parameters
        session: Session
            Database session scope

        user_id: int
            Discord user ID

        char_id: int
            Internal ID of the character

        ### Returns
        CollectedCharacter object with matching ids. None if no match found.
        '''

        found_char = session.execute(
            select(CollectedCharacter)
            .where(CollectedCharacter.owner_id == user_id)
            .where(CollectedCharacter.char_id == char_id)
            ).scalar()
        
        return found_char

    @staticmethod
    def obtain(session: Session, user_id: int, char_id: int, banner_id: int) -> None:
        '''
        Create a new CollectedCharacter instance

        ### Parameters
        session: Session
            Database session scope

        user_id: int
            Discord user ID

        char_id: int
            Internal ID of the character
            
        banner_id: int
            Internal ID of the banner
        '''

        # If already exists, then don't proceed
        if CollectedCharacter.find(session, user_id, char_id) is not None:
            return

        new_char = CollectedCharacter(owner_id = user_id, char_id = char_id, banner_id = banner_id, obtained = datetime.utcnow())
        session.add(new_char)
        session.commit()

    def gain(self, session: Session) -> None:
        '''
        Adds 1 duplicate to this character

        ### Parameters
        session: Session
            Database session scope
        '''

        self.dupes += 1
        session.commit()

    def sell(self, session: Session, amount: int) -> None:
        '''
        Removes a number of duplicates from this character

        ### Parameters
        session: Session
            Database session scope

        amount: int
            Number of duplicates to sell; you cannot sell the first copy

        ### Throws
        InvalidArgumentError
            Provided number is more than the user has to sell
        '''

        # can only sell up to amount of dupes, leaving at least one
        if amount > self.dupes - 1:
            raise InvalidArgumentError
        
        self.dupes -= amount
        session.commit()


