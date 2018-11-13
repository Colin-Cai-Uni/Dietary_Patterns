# Dietary Patterns

A simple repository for holding the scripts used in my thesis, "Data mining authentic, mobile food journals and socio-environmental data". Due to privacy concerns, the dataset itself could not be included in this repository.

## Execution

These were the steps executed during my thesis to run the scripts.

### Global Cleaning and Preprocessing

* All data files (meals.xlsx, questionnaires.csv, and surveys.csv) were placed in the Data directory.
* Extra days were manually removed from questionnaires.csv.
* From the Data directory, liquids.py was run to generate liquids.csv.
* From the Preprocesing directory, global_preprocessing.py was run to generate day_aggregation.csv, meal_aggregation.csv, meal_aggregation_solid.csv, meal_aggregation_liquid.csv, and subject_aggregation.csv.

### Experiment Preprocessing

* From the Experiments/ADC directory, md.sh was run.
* From the Experiments/RNI directory, md.sh was run.
* From the Experiments/MD directory, md.sh was run.

### Experiment Execution

Experiments are stored under four directories:
* Experiments/Raw stores experiments that did not use any feature construction techniques.
* Experiments/ADC stores experiments that used average dietary contribution calculations.
* Experiments/RNI stores experiments that used relative nutritional intake calculations.
* Experiments/MD stores experiments that used macronutrient distribution calculations.

In each directory
* The Key subdirectory performs experiments using only the 8 key dietary intakes with k-means++ and PCA.
* The Full subdirectory performs experiments using all 28 dietary intakes with k-means++ and PCA.
* The Qeustionnaire subdirectory performs experiments using the 8 key dietary intakes and 12 questionnaire response values with k-medoids and Gower's distance metric.

To run an experiment, go to its directory and execute in order:
* cluster.sh
* label.sh (if it exists)
* plot.sh