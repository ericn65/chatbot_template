import matplotlib.pyplot as plt
import numpy as np

class DataVisualization:

    """
    It provides methods to visualize data

    Parameters
    ----------
    TO DEFINE

    Functions
    ---------

    """

    def __init__(self, ):
        pass

    def showBarGraphic(x, y, x_label=None, y_label=None, title=None):
        x = np.array(x)
        y = np.array(y)

        # Check data consistency
        if len(x) != len(y):
            raise ValueError("x and y must have the same length.")

        # Create the plot
        plt.figure(figsize=(10, 6))
        plt.bar(x, y, color='skyblue', edgecolor='black')

        # Labels and title
        if x_label:
            plt.xlabel(x_label, fontsize=12)
        if y_label:
            plt.ylabel(y_label, fontsize=12)
        if title:
            plt.title(title, fontsize=14, fontweight='bold')

        # Rotate labels for readability
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
    
    
    def showLineChart(x, y, x_label=None, y_label=None, title=None):
        """
        Displays a line chart for given labels and values.

        Parameters
        ----------
        TO DEFINE

        Returns
        -------
        None
        """
        x = np.array(x)
        y = np.array(y)

        # Check data consistency
        if len(x) != len(y):
            raise ValueError("x and y must have the same length.")

        # Create the plot
        plt.figure(figsize=(10, 6))
        plt.plot(x, y)

        # Labels and title
        if x_label:
            plt.xlabel(x_label, fontsize=12)
        if y_label:
            plt.ylabel(y_label, fontsize=12)
        if title:
            plt.title(title, fontsize=14, fontweight='bold')

        # Rotate labels for readability
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.grid(True)
        plt.show()


    def showPieChart(labels, values, title=None, colors=None):
        """
        Displays a pie chart for given labels and values.

        Parameters
        ----------
        labels : list, np.ndarray, pd.Series
            Categories or labels.
        values : list, np.ndarray, pd.Series
            Corresponding numeric values.
        title : str, optional
            Title for the chart.
        colors : list, optional
            List of colors for the pie chart.

        Returns
        -------
        None
        """
        # Convert inputs to numpy arrays
        labels = np.array(labels)
        values = np.array(values)

        # Check data consistency
        if len(labels) != len(values):
            raise ValueError("labels and values must have the same length.")

        # Create pie chart
        plt.figure(figsize=(8, 8))
        plt.pie(
            values,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            counterclock=False
        )

        if title:
            plt.title(title, fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.show()

