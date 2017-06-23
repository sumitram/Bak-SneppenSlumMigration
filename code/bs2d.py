'''
A simple Bax-Sneppen 2D model with basic functions to populate and advance the model.

This code was built by Nicky Kessels, Maarten van der Sande, Wessel Klijnsma and Willem Vermeulen,
all master students Computational Science at the University of Amsterdam.
'''

import itertools

from copy import deepcopy
from scipy.stats import multivariate_normal

import numpy as np


class BaxSneppen2D(object):
    '''
    A simple Bax-Sneppen 2D model with basic functions to populate and advance the model.
    '''
    def __init__(self, slum_size=(15, 15), empty_percent=0.3, cell_decrease_factor=0.8):
        # Set the cell decrease factor parameter.
        self.cell_decrease_factor = cell_decrease_factor

        # Set some variables to keep track of the slum.
        self.state = np.ones(slum_size) * 2
        self.ages = np.ones(slum_size) * -1

        # Populate the grid.
        self.populate(empty_percent, slum_size)

        # Normal distribution used to add values to the grid.
        x_mean = slum_size[0]*0.5
        y_mean = slum_size[1]*0.5
        cov = np.array([[x_mean*0.8, 0], [0, y_mean*0.8]])
        self.mvn = multivariate_normal([x_mean, y_mean], cov)

    def populate(self, empty_percent, slum_size):
        '''
        Determines the next slum a cell wants to go to,
        with a preference to cells with cells that are more
        satisfied.

        PARAMETERS
        ===================================================
        empty_percent: float
        The percent of cells which have to become empty.
        Range between 0 and 1.

        slum_size: (int, int)
        The size of the slum which has to be populated.
        '''

        if empty_percent == 1:
            return

        for x_cell in range(slum_size[0]):
            for y_cell in range(slum_size[1]):
                self.state[x_cell][y_cell] = np.random.uniform(0, 1, 1)
                self.ages[x_cell][y_cell] = 0

        empty = np.random.choice(range(slum_size[0] * slum_size[1]),
                                 empty_percent * slum_size[0] * slum_size[1], replace=False)
        for i in empty:
            self.state[i % slum_size[0]][i // slum_size[0]] = 2
            self.ages[i % slum_size[0]][i // slum_size[0]] = -1

    def get_min_val(self):
        '''
        Returns the minimum cell value in the state.

        PARAMETERS
        ===================================================
        None

        RETURNS
        ===================================================
        float
        The minimum cell value in the state. Range between
        0 and 1.
        '''

        return np.min(self.state)

    def get_min_val_index(self):
        '''
        Returns the index of the cell with the minimum cell
        value in the state.

        PARAMETERS
        ===================================================
        None

        RETURNS
        ===================================================
        float
        The index of the cell with the minimum cell value
        in the state.
        '''

        return np.argmin(self.state)

    def get_avg_val(self):
        '''
        Returns the average cell value in the state.

        PARAMETERS
        ===================================================
        None

        RETURNS
        ===================================================
        float
        The average cell value in the state. Range between
        0 and 1.
        '''

        return np.average([i for i in self.state.flatten() if i != 2])

    def has_empty(self):
        '''
        Returns if there is an empty cell in the state.

        PARAMETERS
        ===================================================
        None

        RETURNS
        ===================================================
        boolean
        Whether the state has an empty cell.
        '''

        empty = np.where(self.state == 2)

        if len(empty[0]) == 0:
            return False

        return True

    def add_to_grid(self, previous_value=0):
        '''
        Fills a cell with a higher fitting value than 
        given to the function.

        PARAMETERS
        ===================================================
        previous_value: integer
        The previous value of a cell.

        RETURNS
        ===================================================
        boolean
        Whether the function has succeeded in adding a cell
        to the grid.
        '''

        empty_list = np.where(self.state == 2)

        # Check if there are any cells to fill.
        if len(empty_list[0]) == 0:
            return False

        empty_cells = [(x, y) for x, y in zip(empty_list[0], empty_list[1])]

        # Determine the chances of picking a cell using a 2D normal distribution.
        pvalues = np.array([self.mvn.pdf([empty[0], empty[1]]) for empty in empty_cells])
        pvalues /= np.sum(pvalues)

        # Choose an empty cell and populate it.
        empty_choice = empty_cells[np.random.choice(range(len(empty_cells)), p=pvalues)]

        new_value = 2

        while new_value > 1:
            new_value = abs(np.random.normal(0, (1 - previous_value) / 3.0, 1)) + previous_value

        self.state[empty_choice[0], empty_choice[1]] = new_value
        self.ages[empty_choice[0], empty_choice[1]] = 0

        return True

    def update_ages(self):
        '''
        Update the ages of all cells within the state.

        PARAMETERS
        ===================================================
        None
        '''

        self.ages[np.where(self.ages != -1)] += 1

    def update_state(self, moore=False):
        '''
        Updates the current state. 

        PARAMETERS
        ===================================================
        moore: boolean
        Whether a moore neighbourhood should be used or not.
        '''

        # Build a new state.
        new_state = deepcopy(self.state)

        # Find the current minimum value within the state.
        min_val = np.argmin(new_state)

        x_min = min_val // len(new_state[0])
        y_min = min_val % len(new_state[0])

        # Change the surrounding cells.
        if moore:
            combinations = itertools.product([-1, 0, 1], [-1, 0, 1])
        else:
            combinations = [[-1, 0], [1, 0], [0, -1], [0, 1]]

        for x_mod, y_mod in combinations:
            x_mod = (x_mod + x_min) % len(new_state)
            y_mod = (y_mod + y_min) % len(new_state[0])

            if new_state[x_mod][y_mod] != 2:
                new_state[x_mod][y_mod] *= self.cell_decrease_factor

        # The cell with the minimum value moves to another grid, an empty cell is left.
        new_state[x_min][y_min] = 2
        self.ages[x_min][y_min] = -1

        # Save the state.
        self.state = new_state


def main():
    BaxSneppen2D()

if __name__ == '__main__':
    main()
