# Fell or Found? A data analysis of meteorite landings

Final project for MAT2007 Introduction to Programming (Maastricht Science Programme).

## Research question

How do meteorites that were seen falling differ from meteorites that were found later?

- **Fell** = someone saw the meteorite fall and it was collected after.
- **Found** = the meteorite was found later, nobody saw it fall.

I compare the two groups by how many there are, where they were found (continent) and how heavy they are.

## Dataset

- NASA Meteorite Landings dataset (NASA Open Data Portal, data from the Meteoritical Society)
- Link: https://data.nasa.gov/Space-Science/Meteorite-Landings/gh4g-yrr2
- About 45,700 meteorites
- Columns I use: `fall`, `mass (g)`, `recclass`, `reclat`, `reclong`

Download the CSV from the link and save it as `meteorite_landings.csv` in the same folder as the Python script.

You don't need to clean the data yourself, the script does it:
- for the mass, it only keeps meteorites with a mass above 0
- for the location, it removes missing coordinates, coordinates that are impossible (latitude outside -90/90, longitude outside -180/180) and the point (0, 0), because in this dataset that is used when the location is unknown

## Files

| File | What it is |
|---|---|
| `meteorite_project.py` | the Python script with the whole analysis and all the plots |
| `README.md` | this file |
| `report.pdf` | the 2-page report (made in LaTeX with the course template) |
| `main.tex` | the LaTeX source of the report |
| `plot_continents.png`, `plot_mass_ranges.png` | the two plots used in the report |

## How to run it

1. Install the packages:

   ```
   pip install pandas numpy matplotlib offlineRevGeocoder
   ```

2. Put `meteorite_landings.csv` in the same folder as the script.

3. Run the script in VS Code, or from the terminal:

   ```
   python3 meteorite_project.py
   ```

The plots open one at a time, close one to see the next. The two plots for the report are also saved as PNG files in the same folder. All the numbers (percentages and uncertainties) are printed in the terminal.

Finding the continent for every meteorite can take a few minutes. I tested it with Python 3.14 on macOS. On my laptop it sometimes says "segmentation fault" when the last plot window is closed, but that happens after everything is finished, so the results are not affected.

## What the script does

The plots follow the order of the question: how many → where → how heavy.

1. **Plot 1 – Number:** counts the Found and Fell meteorites and shows the percentage with its uncertainty.
2. **Plot 2 – Continents:** turns latitude/longitude into a continent with `offlineRevGeocoder`. I round the coordinates to 3 decimals and save them in a dictionary, so the same place is not looked up twice (otherwise it was really slow). Then it calculates the percentage of Found and Fell meteorites per continent. Saved as `plot_continents.png`.
3. **Plot 3 – Median mass:** the median mass of Found and Fell meteorites. I used the median and not the mean because a few huge meteorites would push the mean up a lot.
4. **Plot 4 – Mass ranges:** the percentage of each group in 5 mass ranges (< 10 g, 10–100 g, 100 g–1 kg, 1–10 kg, > 10 kg). Saved as `plot_mass_ranges.png`.
5. **Plot 5 (extra) – Classes:** the 6 most common meteorite classes. This one is not in the report.

The percentages are calculated inside each group (so % of all Found and % of all Fell), because there are way more Found than Fell meteorites and comparing the counts directly wouldn't be fair.

For the uncertainty of each percentage I use `sqrt(p * (1 - p) / N)` (the function `percentage_uncertainty` in the code). It is shown as error bars in plots 2, 4 and 5. In plot 1 it is only written in the label, because it is too small to see as a bar.

## Main results

- 97.6% of the meteorites are Found and only 2.4% are Fell.
- Median mass: Fell ≈ 2800 g, Found ≈ 30.5 g.
- About 71% of the Found meteorites (with usable coordinates) come from Antarctica, but 0% of the Fell ones. Fell meteorites come mostly from Europe (34.3%) and Asia (29.5%).
- The error bars are much smaller than the differences between the groups, so the differences are not just random.

My conclusion is that most of these differences come from observational and search bias: big meteorites are easier to see falling in places where people live, while search expeditions (especially in Antarctica) find a lot of small meteorites.

## Use of AI

I used AI (ChatGPT and Claude) to help me with debugging, formatting the plots and checking the text. I checked, ran and changed all the code myself and I can explain every part of it.
