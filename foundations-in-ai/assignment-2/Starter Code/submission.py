import util, math, random
from collections import defaultdict
from util import ValueIteration

############################################################
# Problem 2.2

# If you decide 2.2 is true, prove it in your submission and put "return None" for
# the code blocks below.  If you decide that 2.2 is false, construct a counterexample.
class CounterexampleMDP(util.MDP):
    # Return a value of any type capturing the start state of the MDP.
    def startState(self):
        # BEGIN_YOUR_CODE 
        return 0  # Start at state 0
        # END_YOUR_CODE

    # Return a list of strings representing actions possible from |state|.
    def actions(self, state):
        # BEGIN_YOUR_CODE 
        # Different states could potentially have different actions
        if state == 4:  # Terminal state
            return []  # No actions possible in terminal state
        else:
            return ['A', 'B']  # All other states have both actions available
        # END_YOUR_CODE

    # Given a |state| and |action|, return a list of (newState, prob, reward) tuples
    # corresponding to the states reachable from |state| when taking |action|.
    # Remember that if |state| is an end state, you should return an empty list [].
    def succAndProbReward(self, state, action):
        # BEGIN_YOUR_CODE 
        if state == 0:
            if action == 'A':
                return [(1, 0.5, math.log(2)), (2, 0.5, math.log(2))]
            else:  # action == 'B'
                return [(3, 1.0, math.log(2))]
        elif state in [1, 2]:
            return [(4, 1.0, math.log(11))]  # ~= 10 reward
        elif state == 3:
            return [(4, 1.0, 0)]
        else:  # state == 4 (terminal state)
            return []
        # END_YOUR_CODE

    # Set the discount factor (float or integer) for your counterexample MDP.
    def discount(self):
        # BEGIN_YOUR_CODE 
        return 0.5  # Discount factor less than 1
        # END_YOUR_CODE

############################################################
# Problem 3

class BlackjackMDP(util.MDP):
    def __init__(self, cardValues, multiplicity, threshold, peekCost):
        """
        cardValues: list of integers (face values for each card included in the deck)
        multiplicity: single integer representing the number of cards with each face value
        threshold: maximum number of points (i.e. sum of card values in hand) before going bust
        peekCost: how much it costs to peek at the next card
        """
        self.cardValues = cardValues
        self.multiplicity = multiplicity
        self.threshold = threshold
        self.peekCost = peekCost

    # Return the start state.
    # Look closely at this function to see an example of state representation for our Blackjack game.
    # Each state is a tuple with 3 elements:
    #   -- The first element of the tuple is the sum of the cards in the player's hand.
    #   -- If the player's last action was to peek, the second element is the index
    #      (not the face value) of the next card that will be drawn; otherwise, the
    #      second element is None.
    #   -- The third element is a tuple giving counts for each of the cards remaining
    #      in the deck, or None if the deck is empty or the game is over (e.g. when
    #      the user quits or goes bust).
    def startState(self):
        return (0, None, (self.multiplicity,) * len(self.cardValues))

    # Return set of actions possible from |state|.
    # You do not need to modify this function.
    # All logic for dealing with end states should be placed into the succAndProbReward function below.
    def actions(self, state):
        return ['Take', 'Peek', 'Quit']

    # Given a |state| and |action|, return a list of (newState, prob, reward) tuples
    # corresponding to the states reachable from |state| when taking |action|.
    # A few reminders:
    # * Indicate a terminal state (after quitting, busting, or running out of cards)
    #   by setting the deck to None.
    # * If |state| is an end state, you should return an empty list [].
    # * When the probability is 0 for a transition to a particular new state,
    #   don't include that state in the list returned by succAndProbReward.
    def succAndProbReward(self, state, action):
        """
        Returns list of (newState, prob, reward) tuples corresponding to the states reachable
        from |state| when taking |action|.
        
        Args:
            state: Tuple of (totalCardValueInHand, nextCardIndexIfPeeked, deckCardCounts)
            action: String - one of ['Take', 'Peek', 'Quit']
        """
        # BEGIN_YOUR_CODE 
        totalValue, nextCardIndex, deckCards = state
        
        # If we're in an end state (deck is None), return empty list
        if deckCards is None:
            return []
            
        # Convert deckCards to list for easier manipulation
        deckCardsList = list(deckCards)
        
        # Handle 'Quit' action
        if action == 'Quit':
            return [((totalValue, None, None), 1.0, totalValue)]
        
        # Handle 'Peek' action
        if action == 'Peek':
            # Can't peek if we just peeked
            if nextCardIndex is not None:
                return []
                
            successors = []
            remaining_cards = sum(deckCardsList)
            if remaining_cards == 0:  # No cards left to peek at
                return []
                
            # For each possible card we could peek at
            for cardIndex, count in enumerate(deckCardsList):
                if count > 0:
                    prob = float(count) / remaining_cards
                    newState = (totalValue, cardIndex, deckCards)
                    successors.append((newState, prob, -self.peekCost))
                    
            return successors
        
        # Handle 'Take' action
        if action == 'Take':
            successors = []
            
            # If we previously peeked, we must take that card
            if nextCardIndex is not None:
                if deckCardsList[nextCardIndex] <= 0:  # Sanity check
                    return []
                    
                # Take the card we peeked at
                newValue = totalValue + self.cardValues[nextCardIndex]
                newDeckCards = list(deckCards)
                newDeckCards[nextCardIndex] -= 1
                
                # If we went bust
                if newValue > self.threshold:
                    return [((newValue, None, None), 1.0, 0)]
                    
                # If no cards left
                if sum(newDeckCards) == 0:
                    return [((newValue, None, None), 1.0, newValue)]
                    
                return [((newValue, None, tuple(newDeckCards)), 1.0, 0)]
                
            # If we didn't peek, consider all possible cards
            remaining_cards = sum(deckCardsList)
            if remaining_cards == 0:  # No cards left to take
                return []
                
            # For each possible card we could draw
            for cardIndex, count in enumerate(deckCardsList):
                if count > 0:
                    prob = float(count) / remaining_cards
                    newValue = totalValue + self.cardValues[cardIndex]
                    newDeckCards = list(deckCards)
                    newDeckCards[cardIndex] -= 1
                    
                    # If we went bust
                    if newValue > self.threshold:
                        successors.append(((newValue, None, None), prob, 0))
                        continue
                        
                    # If no cards left
                    if sum(newDeckCards) == 0:
                        successors.append(((newValue, None, None), prob, newValue))
                        continue
                        
                    successors.append(((newValue, None, tuple(newDeckCards)), prob, 0))
                    
            return successors
            
        return []  # Invalid action
        # END_YOUR_CODE

    def discount(self):
        return 1

############################################################
# Problem 3b

def peekingMDP():
    """
    Return an instance of BlackjackMDP where peeking is the
    optimal action at least 10% of the time.
    """
    # BEGIN_YOUR_CODE 
    # Key idea: We want more states where we have accumulated enough value
    # that it's worth peeking to avoid busting, but not so much value
    # that we should just quit
    cardValues = [3, 4, 19]
    multiplicity = 4
    threshold = 20.0
    peekCost = 1.0
    
    # This creates many states where:
    # - Can safely build value with 3s and 4s
    # - After ~6-15 points, a 19 would bust you
    # - Multiple safe options after peeking at a 19
    # - More total cards means more decision points
    
    return BlackjackMDP(cardValues, multiplicity, threshold, peekCost)
    # END_YOUR_CODE