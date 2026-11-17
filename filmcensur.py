import pandas as pd
import argparse
import random
from prettytable import PrettyTable


def main(argv=None):
    args = parse_args(argv)
    film_registry = read_film_registry()

    # Check if random first since that excludes the potential -t "title" input from a user
    if args.r != None:
        title = get_random_title(film_registry)
    elif args.t != None:
        title = args.t
    else:
        # If no additional command-line argument is give, get the title from the user through the terminal
        title = input("Vad är filmens titel? ")

    # Normalize the user input to avoid instance where the key might not be found
    title = title.lower()
    film_key = get_primary_key(film_registry, title)
    cuts, category, year, country = get_other_info(film_registry, film_key)
    summary = f"Filmen '{title.capitalize()}', är av kategori {category.lower()} från {year} producerad i {country}"

    # If there have been cuts, the program also gathers information about these cuts from the registry file of all the cuts that were made by the bureau
    if cuts != 0:
        cuts_registry = read_cuts_registry()
        found_cuts = find_cuts(cuts_registry, film_key)
        table = write_to_table(found_cuts)
        print(f"Movie: {title}")
        while True:
            answer = input("Vill du spara dina resultat i en .txt-fil? (y/n) ")

            if answer == "y":
                print(f"Saving your results to filename: {film_key}.txt")
                write_to_txt(film_key, summary, table)
                return False

            elif answer == "n":
                print(f"{summary} was cut {cuts} times")
                print(table)
                return False

            else:
                print("Not a valid input")
    # If there were no cuts, there's no point in checking the registry file for cuts made
    else:
        print(summary)
        print(f"No cuts were made.")


def parse_args(argv=None):
    """
    Handles extended use of command-line arguments when running the program.
    By default returns None.
    """
    parser = argparse.ArgumentParser(
        description="Handles two variants of the program, -r (random) OR  -t (title). A value for -r overrides any title given in -t but does not produce any errors."
    )

    parser.add_argument(
        "-r",
        type=int,
        help="Gives the user a random movie entry if -r is followed by any integer value."
    )

    parser.add_argument(
        "-t",
        type=str,
        help="Specifies which title the user wants information about, -t 'askungen'"
    )

    return parser.parse_args(argv)


def read_film_registry(filename="FILMREG.csv") -> pd.DataFrame:
    """
    Reads the CSV file containing the complete registry and return it as a DataFrame.
    This file uses ";" as a separator and cp1252 as the encoding.
    """
    try:
        df = pd.read_csv(
            filename,
            header=0,
            on_bad_lines="skip",
            encoding="cp1252",
            sep=";",
            dtype="str"
        )
    except FileNotFoundError:
        print(f"En CSV-fil med namn: {filename} kunde inte hittas.")
        raise FileNotFoundError

    # The check is in place to avoid a UnboundLocalError if the file FILMREG.csv is not read, since these columns only exist in that file
    if filename == "FILMREG.csv":
        # Clears a few colums that are not used and are called Unnamed: [number] that otherwise create DtypeWarnings
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

    return df


def get_random_title(df: pd.DataFrame) -> str:
    """
    Produces a random index number used to find a row in the dataframe.
    Returns the title of the movie that is located on that row.
    """
    random_index = random.randint(0, len(df) - 1)
    row = df.iloc[random_index]
    title = row["Titel_Org"]

    return title


def read_cuts_registry(filename="klipp.csv") -> pd.DataFrame:
    """
    Reads the CSV file containing the register of cuts and return it as a DataFrame.
    This file uses "," as a separator and utf-8 as the encoding.
    The original file from Riksarkivet did not include a header row in the file, I added one for this iteration of the file based on the description of the dataset.
    """
    try:
        df = pd.read_csv(
            filename,
            header=0,
            on_bad_lines="skip",
            encoding="utf-8",
            sep=","
        )
    except FileNotFoundError:
        print(f"En CSV-fil med namn: {filename} kunde inte hittas.")
        raise FileNotFoundError

    return df


def get_primary_key(df: pd.DataFrame, title: str) -> str:
    """
    Takes the registry as a dataframe and the title of the movie and returns the value for "Granskningsnummer" from that same row in the dataframe.
    This value is the primary key for that movie.
    Returns the primary key value as a str.
    """
    try:
        matches = df[(df["Titel_Org"].str.lower() == title) |
                     (df["Titel_Svensk"].str.lower() == title)]
    except KeyError:
        raise KeyError("That column is not in the registry.")

    if matches.empty:
        raise ValueError("That movie is not in the registry.")

    row = matches.iloc[0]
    key = row["Granskningsnummer"]

    return key


def get_other_info(df: pd.DataFrame, key: str):
    """
    Takes the registry as a dataframe and the primary key for the movies.
    Returns values for an int of how many cuts were made and strs for the film category, the year it was produced and the country is was produced in.
    Refer to the description of the data-set for other possible values that could be gathered by this function
    """
    matches = df[(df["Granskningsnummer"] == key)]
    row = matches.iloc[0]
    try:
        cuts = int(row["Klipp_Antal"])
    except ValueError:
        raise ValueError("Inte ett giltigt värde för antalet klipp för denna film.")
    category = row["Filmkategori"]
    year = row["Produktionsaar"]
    country = row["Produktionsland"]

    return cuts, category, year, country


def find_cuts(df: pd.DataFrame, film_key: str):
    """
    Takes the registry of cuts as a dataframe and the primary key of the movie as input.
    Returns a dictionary that contains more info about the cuts that were made for the movie.
    """
    try:
        matches = df[(df["Granskningsnummer"] == film_key)]
    except KeyError:
        raise KeyError("Kolumnen finns inte i registret.")

    return matches[["Bortklippt_beskrivning", "Motiv", "AAtgaerd"]].to_dict(orient="records")


def write_to_table(list_object):
    """
    The function takes a list of dictionaries with data regarding the cuts made to the movie.
    The function returns an object of the PrettyTable class that can then be printed to the terminal or written to a file.
    """
    # The original names of the headers are replaced with its corresponding field description given for the dataset
    field_names = {
        "Bortklippt_beskrivning": "Beskrivning av bortklippt del",
        "Motiv": "Motivering för censur-klipp",
        "AAtgaerd": "Beslutad åtgärd"
    }

    table = PrettyTable()

    # Use the values from the columns in the first row as the headers
    header_row = list(list_object[0].keys())

    # Use the values from field_names instead of its key as the text given in the output
    table.field_names = [field_names.get(h, h) for h in header_row]

    # Add each dict from the list_object to the table object, replace the output value for each header
    for row in list_object:
        table.add_row([row.get(h, "") for h in header_row])

    return table


def write_to_txt(key: int, summary: str, table) -> None:
    """
    The function takes the primary key of the movie, a summary of it and the table object with information about the cuts that were made as input.
    It writes this to a file of the same name as the primary key of the movie.
    """
    with open(f"{key}.txt", "w") as file:
        file.write(f"{summary}\n{table}")


if __name__ == "__main__":
    main()
