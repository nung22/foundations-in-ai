# Name: Nicholas Ung
# Email: ung.n@northeastern.edu
# NUID: 002336960

from typing import List, Tuple

from mapUtil import (
    CityMap,
    computeDistance,
    createSanJoseMap,
    locationFromTag,
    makeTag, getTotalCost,
)
from util import Heuristic, SearchProblem, State, UniformCostSearch


# *IMPORTANT* :: A key part of this assignment is figuring out how to model states
# effectively. We've defined a class `State` to help you think through this, with a
# field called `memory`.
#
# As you implement the different types of search problems below, think about what
# `memory` should contain to enable efficient search!
#   > Please read the docstring for `State` in `util.py` for more details and code.

# Please also read the docstrings for the relevant classes and functions defined in `mapUtil.py`

########################################################################################
# Problem 1a: Modeling the Shortest Path Problem.


class ShortestPathProblem(SearchProblem):
    """
    Defines a search problem that corresponds to finding the shortest path
    from `startLocation` to any location with the specified `endTag`.
    """

    def __init__(self, startLocation: str, endTag: str, cityMap: CityMap):
        self.startLocation = startLocation
        self.endTag = endTag
        self.cityMap = cityMap

    def startState(self) -> State:
        # BEGIN_YOUR_CODE 

        # Initialize starting state with just the location
        # No memory needed because we only care about the shortest path
        return State(location=self.startLocation)

        # END_YOUR_CODE

    def isEnd(self, state: State) -> bool:
        # BEGIN_YOUR_CODE 

        # Check if the current location has the target endTag among its tags
        # Return true if we've reached a valid end location
        return self.endTag in self.cityMap.tags[state.location]

        # END_YOUR_CODE

    def successorsAndCosts(self, state: State) -> List[Tuple[str, State, float]]:
        """
        Note we want to return a list of *3-tuples* of the form:
            (successorLocation: str, successorState: State, cost: float)
        """
        # BEGIN_YOUR_CODE 

        successors = []
        # Look upp all the locations connected to the current location in cityMap
        for nextLocation, distance in self.cityMap.distances[state.location].items():
            # Create a new state with only the next location
            nextState = State(nextLocation)
            # Add successor with action => nextLocation, newState, and cost => distance
            successors.append((nextLocation, nextState, distance))
        return successors

        # END_YOUR_CODE


########################################################################################
# Problem 1b: Custom -- Plan a Route through San Jose


def getSanJoseShortestPathProblem() -> ShortestPathProblem:
    """
    Create your own search problem using the map of San Jose, specifying your own
    `startLocation`/`endTag`. If you prefer, you may create a new map using via
    `createCustomMap()`.

    Run `python mapUtil.py > readableSanJoseMap.txt` to dump a file with a list of
    locations and associated tags; you might find it useful to search for the following
    tag keys (amongst others):
        - `landmark=` - Hand-defined landmarks (from `data/sanjose-landmarks.json`)
        - `amenity=`  - Various amenity types (e.g., "parking_entrance", "food")
        - `parking=`  - Assorted parking options (e.g., "underground")
    """
    cityMap = createSanJoseMap()

    # Or, if you would rather use a custom map, you can uncomment the following!
    # cityMap = createCustomMap("data/custom.pbf", "data/custom-landmarks".json")

    # BEGIN_YOUR_CODE (our solution is 2 lines of code, but don't worry if you deviate from this)

    # Get start location from a known landmark - using the Northeastern Building
    startLocation = locationFromTag(makeTag("landmark", "northeastern_building"), cityMap)
    # Set end tag to another landmark - going to Starbucks
    endTag = makeTag("landmark", "starbucks")

    return ShortestPathProblem(startLocation, endTag, cityMap)

    # END_YOUR_CODE


########################################################################################
# Problem 2a: Modeling the Waypoints Shortest Path Problem.


class WaypointsShortestPathProblem(SearchProblem):
    """
    Defines a search problem that corresponds to finding the shortest path from
    `startLocation` to any location with the specified `endTag` such that the path also
    traverses locations that cover the set of tags in `waypointTags`.

    Hint: naively, your `memory` representation could be a list of all locations visited.
    However, that would be too large of a state space to search over! Think 
    carefully about what `memory` should represent.
    """
    def __init__(
        self, startLocation: str, waypointTags: List[str], endTag: str, cityMap: CityMap
    ):
        self.startLocation = startLocation
        self.endTag = endTag
        self.cityMap = cityMap

        # We want waypointTags to be consistent/canonical (sorted) and hashable (tuple)
        self.waypointTags = tuple(sorted(waypointTags))

    def startState(self) -> State:
        # BEGIN_YOUR_CODE 

        # Check if start location satisfies any waypoints
        start_waypoints = frozenset(tag for tag in self.cityMap.tags[self.startLocation] if tag in self.waypointTags)
        # Initialize state with starting location and any waypoints it covers
        return State(self.startLocation, memory=start_waypoints)

        # END_YOUR_CODE

    def isEnd(self, state: State) -> bool:
        # BEGIN_YOUR_CODE

        # Two conditions need to be met:
        # 1. Current location has the endTag
        # 2. All required waypoints have been visited (stored in memory)
        has_end_tag = self.endTag in self.cityMap.tags[state.location]
        all_waypoints_visited = all(waypoint in state.memory for waypoint in self.waypointTags)
        return has_end_tag and all_waypoints_visited

        # END_YOUR_CODE

    def successorsAndCosts(self, state: State) -> List[Tuple[str, State, float]]:
        # BEGIN_YOUR_CODE 

        successors = []
        # Get all connected locations and their distances
        for nextLoc, distance in self.cityMap.distances[state.location].items():
            # Find any waypointTags at the next location
            current_waypoints = frozenset(tag for tag in self.cityMap.tags[nextLoc] if tag in self.waypointTags)
            # Combine previously visited waypoints with new ones
            updated_waypoints = state.memory.union(current_waypoints)
            # Create new state with updated location and waypoints
            nextState = State(nextLoc, memory=updated_waypoints)
            successors.append((nextLoc, nextState, distance))
        return successors

        # END_YOUR_CODE


########################################################################################
# Problem 2b: Custom -- Plan a Route with Unordered Waypoints through San Jose

def getSanJoseWaypointsShortestPathProblem() -> WaypointsShortestPathProblem:
    """
    Create your own search problem using the map of San Jose, specifying your own
    `startLocation`/`waypointTags`/`endTag`.

    Similar to Problem 1b, use `readableSanJoseMap.txt` to identify potential
    locations and tags.
    """
    cityMap = createSanJoseMap()
    # BEGIN_YOUR_CODE (our solution is 4 lines of code, but don't worry if you deviate from this)

    # Get start location - starting at northeastern building
    startLocation = locationFromTag(makeTag("landmark", "northeastern_building"), cityMap)

    # Define waypoint tags to visit - multiple landmarks to pass through
    waypointTags = [
        makeTag("landmark", "philz"),
        makeTag("landmark", "san_pedro_market"),
        makeTag("landmark", "city_hall")
    ]

    # Set end destination
    endTag = makeTag("landmark", "bus_station")

    # END_YOUR_CODE
    return WaypointsShortestPathProblem(startLocation, waypointTags, endTag, cityMap)

########################################################################################
# Problem 4a: A* to UCS reduction

# Turn an existing SearchProblem (`problem`) you are trying to solve with a
# Heuristic (`heuristic`) into a new SearchProblem (`newSearchProblem`), such
# that running uniform cost search on `newSearchProblem` is equivalent to
# running A* on `problem` subject to `heuristic`.
#
# This process of translating a model of a problem + extra constraints into a
# new instance of the same problem is called a reduction; it's a powerful tool
# for writing down "new" models in a language we're already familiar with.
# See util.py for the class definitions and methods of Heuristic and SearchProblem.


def aStarReduction(problem: SearchProblem, heuristic: Heuristic) -> SearchProblem:
    class NewSearchProblem(SearchProblem):
        def startState(self) -> State:
            # BEGIN_YOUR_CODE

            # A* uses same start state as original problem
            return problem.startState()

            # END_YOUR_CODE

        def isEnd(self, state: State) -> bool:
            # BEGIN_YOUR_CODE

            # End condition remains the same as original problem
            return problem.isEnd(state)

            # END_YOUR_CODE

        def successorsAndCosts(self, state: State) -> List[Tuple[str, State, float]]:
            # BEGIN_YOUR_CODE

            # Get successors from original problem
            successors = []
            for action, nextState, cost in problem.successorsAndCosts(state):
                # Modify cost to include heuristic estimate for A*
                # f(n) = g(n) + h(n) where:
                # g(n) = cost to reach node (original cost)
                # h(n) = estimated cost to goal (heuristic)
                newCost = cost + heuristic.evaluate(nextState)
                successors.append((action, nextState, newCost))
            return successors

            # END_YOUR_CODE

    return NewSearchProblem()


########################################################################################
# Problem 4b: "straight-line" heuristic for A*


class StraightLineHeuristic(Heuristic):
    """
    Estimate the cost between locations as the straight-line distance.
        > Hint: you might consider using `computeDistance` defined in `mapUtil.py`
    """
    def __init__(self, endTag: str, cityMap: CityMap):
        self.endTag = endTag
        self.cityMap = cityMap

        # Precompute all the Geolocations associated with endTag
        # BEGIN_YOUR_CODE

        # Find all locations that have the endTag and store their locations
        self.endLocations = []
        for location, tags in self.cityMap.tags.items():
            if self.endTag in tags:
                self.endLocations.append(location)

        # END_YOUR_CODE

    def evaluate(self, state: State) -> float:
        # BEGIN_YOUR_CODE

        # If no end locations found, return 0
        if not self.endLocations:
            return 0.0

        # Get current location's coordinates
        currentLocation = self.cityMap.geoLocations[state.location]

        # Find minimum straight-line distance to any end location
        min_distance = float('inf')
        for endLoc in self.endLocations:
            endLocation = self.cityMap.geoLocations[endLoc]
            distance = computeDistance(currentLocation, endLocation)
            min_distance = min(min_distance, distance)

        return min_distance

        # END_YOUR_CODE