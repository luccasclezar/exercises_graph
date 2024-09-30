from datetime import datetime
import os
import re
from typing import List
import pandas as pd
import altair as alt

# TODO: There should be a way to update this by date.
bodyWeight = 75


class Set:
    """Each set in an exercise day.

    The format for a set is: 1x10x100

    where:
      - The first number is the number of sets;
      - The second number is the number of reps;
      - And the third number is the weight (if absent, bodyWeight var is used).

    Sets with rest-pauses are written in between square-brackets,
    like: [1x10x100, 1x4x100, 1x2x100]."""

    def __init__(self, setString: str):
        setArr = setString.split(' = ')[0].split('x')

        self.timesDone = int(setArr[0])
        self.reps = int(setArr[1])
        self.load = bodyWeight

        # If there is a third number in the
        if setArr.__len__() > 2:
            self.load = int(re.sub(r'[^\d]', '', setArr[2]))

        self.total = self.timesDone * self.reps * self.load


    def __str__(self):
        return str(self.__dict__)
    def __repr__(self):
        return self.__str__()


class Exercise:
    """Each exercise in a day, with any number of sets.

    The format for an exercise in a day is:

    Bench Press - 1x12x50, 2x10x50"""

    def __init__(self, exerciseStr: str):
        nameAndSets = exerciseStr.split(' - ')
        self.name = nameAndSets[0]

        self.sets: List[Set] = []

        # Process each set.
        for setStr in nameAndSets[1].split(', '):
            self.sets.append(Set(setStr))

        # Sum the total of all sets to have the exercise's total.
        self.total = sum([s.total for s in self.sets])

    def __str__(self):
        return str(self.__dict__)
    def __repr__(self):
        return self.__str__()


class ExerciseDay:
    """Each day of exercise done.

    The format for a day of exercise is:
    <br>
    <br>
    <br>
    01/01/1970\n
    Exercise 1 - 3x10x50\n
    Exercise 2 - 3x10x50\n
    [other exercises]"""

    def __init__(self, dayText: str):
        dayArray = dayText.split('\n')

        # If there's a "(C)" right after the date, this is a calisthenics day,
        # and should be differentiated from gym days.
        self.isCalisthenics = dayArray[0].__contains__('(C)')

        # Date should be formatted as DD/MM/YYYY, and after processing it, we
        # discard the first item in dayArray to keep only the exercises.
        self.date = datetime.strptime(dayArray[0][0:10], '%d/%m/%Y')
        dayArray.remove(dayArray[0])

        self.exercises: List[Exercise] = []

        # Now we need to process the exercises
        for exerciseStr in dayArray:
            # If this line starts with "Total" or is empty, we should just ignore it.
            if exerciseStr.startswith('Total') or exerciseStr.__len__() == 0:
                continue

            # Process the Exercise.
            self.exercises.append(Exercise(exerciseStr))

        # Sum the total of all exercises to get the day's total.
        self.total = sum([e.total for e in self.exercises])

    def __str__(self):
        return str(self.__dict__)
    def __repr__(self):
        return self.__str__()


def chartFile(fileName: str):
    file = open(fileName)
    fileText = file.read()

    # Remove lines starting with "*", and remove brackets as rest-pause doesn't make a difference
    # in the total weight lifted in the day.
    exerciseDaysStr = re.sub(r'\*.+?\n\n', '', fileText.replace('[', '').replace(']', '')).split('\n\n')
    exerciseDays: List[ExerciseDay] = []

    # Process each exercise day.
    for exerciseDayStr in exerciseDaysStr:
        exerciseDays.append(ExerciseDay(exerciseDayStr))

    # Set the chart's variables.
    dates = [d.date for d in exerciseDays]
    colors = [('#ff0000' if d.isCalisthenics else '#000000') for d in exerciseDays]
    totals = [d.total for d in exerciseDays]

    df = pd.DataFrame({
        'Dates': dates,
        'Colors': colors,
        'Total Load': totals,
    })

    # Create the actual chart with "Dates" on the X axis and "Total Load" on the Y axis.
    chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X('Dates', axis=alt.Axis()),
        y=alt.Y('Total Load'),
        ).properties(
            # The width should be relative to how many points on the X axis the chart has.
            width=len(exerciseDays) * 64
        )

    # Add labels for each date.
    text = chart.mark_text(dy=12).encode(text='Dates', color=alt.Color('Colors:N', scale=None))

    if not os.path.exists('out/'):
        os.makedirs('out/')

    # Save the chart as png.
    (chart + text).save('out/' + fileName.split('.')[0] + '.png')

# Create a chart for each type of training.
chartFile('push.txt')
chartFile('pull.txt')
chartFile('legs.txt')
