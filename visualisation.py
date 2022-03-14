import matplotlib.pyplot as plt
import os
from enums import Experiment, ExperimentType
from genetic import load_simulation_info
import numpy as np


def graph_plot(ax, generations, data, colour_map, graph_type, iteration_num, exp, exp_type, plot_std=False, stds=None):
    ax.set_xlabel('Generations')
    ax.set_ylabel('Average of ' + graph_type.capitalize() +
                  ' Fitness over ' + str(iteration_num) + ' iterations')
    for i in range(len(data)):
        if exp == Experiment.CXINDPB and exp_type == ExperimentType.FINAL:
            colour = "#9701FF" if i == 1 else "#00C5FF"
        elif exp == Experiment.INPUT and exp_type == ExperimentType.FINAL:
            colour = "#20FF00" if i == 1 else "#FFAD54"
        elif exp == Experiment.FINAL_ALGORITHM:
            colour = "#557FFF"
        else:
            colour = colour_map(1.*data.index(data[i])/len(data))

        gen = generations
        ax.plot(gen, data[i][1], lw=3, label=data[i][0], color=colour)
        if graph_type == "mean" and plot_std:
            ax.fill_between(
                gen, (data[i][1]+stds[i][1]), (data[i][1]-stds[i][1]), color=colour, alpha=.1)

    ax.legend(loc='best', fancybox=True, framealpha=0.5)


def box_plot(ax, input, colour_map, exp, exp_type):
    labels = [algorithm[0] for algorithm in input]
    data = [algorithm[1] for algorithm in input]
    ax.set_xlabel('Algorithm Parameters')
    ax.set_ylabel('Fitness')
    labels = [label[:11] + "\n" + label[12:] for label in labels]
    box_plots = ax.boxplot(data, patch_artist=True, labels=labels)

    for i, plot in enumerate(box_plots['boxes']):
        if exp == Experiment.CXINDPB and exp_type == ExperimentType.FINAL:
            colour = "#9701FF" if i == 1 else "#00C5FF"
        elif exp == Experiment.INPUT and exp_type == ExperimentType.FINAL:
            colour = "#20FF00" if i == 1 else "#FFAD54"
        elif exp == Experiment.FINAL_ALGORITHM:
            colour = "#557FFF"
        else:
            colour = colour_map(1.*data.index(data[i])/len(data))

        plot.set_facecolor(colour)


def initialise_graphs():
    fig = plt.figure(figsize=(14, 10), dpi=80)
    ax1 = plt.subplot(221)
    ax2 = plt.subplot(222, sharey=ax1)
    ax3 = plt.subplot(212)
    fig.set_size_inches(30, 20)
    fig.tight_layout()
    plt.subplots_adjust(left=0.125, bottom=0.1, right=0.9,
                        top=0.9, wspace=0.1, hspace=0.1)
    return fig, ax1, ax2, ax3


def plot_experiment(exp, exp_type, plot_std=False):
    if exp_type == ExperimentType.EXPLORATION:
        iteration_num = 5
    elif exp_type == ExperimentType.FINAL:
        iteration_num = 15
    elif exp_type == ExperimentType.FINAL_ALGORITHM:
        iteration_num = 20

    fig, ax1, ax2, ax3 = initialise_graphs()

    if exp == Experiment.CXINDPB:
        suptitle = f"{exp_type.value.capitalize()} experiment showing the effect of different mutation and crossover probabilities on fitness over 150 generations"
    elif exp == Experiment.INPUT:
        suptitle = f"{exp_type.value.capitalize()} experiment showing the effect of different neural network inputs on fitness over 150 generations"
    elif exp == Experiment.FINAL_ALGORITHM:
        suptitle = "Final algorithm's fitnessees over 250 generations"

    fig.suptitle(suptitle)

    if exp != Experiment.FINAL_ALGORITHM:
        save_location = f"sim-outputs//{exp.value}-{exp_type.value}-experiment"
    else:
        save_location = f"sim-outputs//{exp.value}"

    averaged_means, averaged_maxes, averaged_stds = ([] for _ in range(3))
    final_generation_averages = []

    if exp != Experiment.FINAL_ALGORITHM:
        alterations = [folder for folder in os.listdir(
            save_location) if os.path.isdir(save_location + "//" + folder)]
    else:
        alterations = range(1)

    for alteration in alterations:
        if exp != Experiment.FINAL_ALGORITHM:
            iterations = load_simulation_info(
                save_location + "//" + alteration)
        else:
            iterations = load_simulation_info(save_location)

        logbooks = [run[1] for run in iterations]

        means, maxes, stds = ([] for _ in range(3))
        final_averages = []

        for logbook in logbooks:
            means.append(logbook.select("mean"))
            maxes.append(logbook.select("max"))
            stds.append(logbook.select("std"))
            final_averages.append(logbook.select("mean")[-1])

        label = iterations[0][0]
        averaged_means.append((label, np.mean(means, axis=0)))
        averaged_maxes.append((label, np.mean(maxes, axis=0)))
        averaged_stds.append((label, np.mean(stds, axis=0)))
        final_generation_averages.append((label, final_averages))

    ax1.title.set_text("Mean fitness over all generations")
    graph_plot(ax1, logbooks[0].select("gen"), averaged_means, plt.get_cmap(
        "gist_rainbow"), "mean", iteration_num, exp, exp_type, plot_std, averaged_stds)

    ax2.title.set_text("Max fitness over all generations")
    graph_plot(ax2, logbooks[0].select("gen"), averaged_maxes, plt.get_cmap(
        "gist_rainbow"), "max", iteration_num, exp, exp_type)

    ax3.title.set_text(
        "Distribution of the average fitness values from the final generation of each iteration")
    box_plot(ax3, final_generation_averages,
             plt.get_cmap("gist_rainbow"), exp, exp_type)

    if exp != Experiment.FINAL_ALGORITHM:
        plt.savefig(save_location +
                    f"//{exp.value}-{exp_type.value}-graphs.png")
    else:
        plt.savefig(save_location + f"//{exp.value}-graphs.png")
