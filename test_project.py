from project import parse_args, read_film_registry, get_random_title, read_cuts_registry, get_primary_key, get_other_info, find_cuts, write_to_table, write_to_txt
import pytest
import pandas as pd
import os


def test_parse_args_r():
    """
    Tests that the function correctly handles the "-r" argument.
    """
    args = parse_args(["-r", "1"])

    assert args.r == 1


def test_parse_args_t():
    """
    Tests that the function correctly handles the "-t" argument.
    """
    args = parse_args(["-t", "askungen"])

    assert args.t == "askungen"


def test_parse_args_undefined():
    """
    There exists no "-p" argument for the function, so the test asserts that the function returns an exit value code of "2".
    """
    with pytest.raises(SystemExit) as exc:
        parse_args(["-p", "wrong"])

    assert exc.value.code == 2


def test_parse_args_default_is_none():
    """
    Test that the function correctly has "None" as a default value.
    """
    assert parse_args.__defaults__ == (None,)


def test_read_film_registry_wrong_file():
    """
    Tests that the function correctly handles the possibility that the wrong file is given as input.
    """
    with pytest.raises(FileNotFoundError):
        read_film_registry("FEL_FIL.csv")


def test_read_film_registry_df():
    """
    Tests that all the columns that are used from the file are found in it.
    """
    df = read_film_registry()

    # These are all the columns in the df that are used by other functions in the program, and so need to be found in the df
    used_columns = {
        "Titel_Svensk",
        "Titel_Org",
        "Granskningsnummer",
        "Klipp_Antal",
        "Filmkategori",
        "Produktionsaar",
        "Produktionsland",
    }

    # If a column is used but missing from the df, the test provides info of which column is missing
    missing_columns = used_columns - set(df.columns)

    assert not missing_columns, f"Missing columns: {missing_columns}"


def test_get_random_title_is_in_df():
    """
    Tests if the function returns a title from the dataframe.
    Does not test the randomness of the call.
    """
    titles = ["Faust Sonnengesang", "Presents", "Odyssey, The"]

    # Create a df with one column and the rows in titles that the function uses
    df = pd.DataFrame({"Titel_Org": titles})

    title = get_random_title(df)

    assert title in titles


def test_read_cuts_registry_wrong_file():
    """
    Tests that the function correctly handles the possibility that the wrong file is given as input.
    """
    with pytest.raises(FileNotFoundError):
        read_cuts_registry("FEL_FIL.csv")


def test_read_cuts_registry_df():
    """
    Tests that all the columns that are used from the file are found in it.
    """
    df = read_cuts_registry()

    # These are all the columns in the df that are used by other functions in the program, and so need to be found in the df
    used_columns = {
        "Granskningsnummer",
        "Motiv",
        "AAtgaerd"
    }

    # If a column is used but missing from the df, the test provides info of which column is missing
    missing_columns = used_columns - set(df.columns)

    assert not missing_columns, f"Missing columns: {missing_columns}"


def test_get_primary_key():
    """
    Tests that the function gets the primary key from the corresponding title, and not from some other title.
    """
    df = pd.DataFrame(
        {
            "Titel_Org": ["Faust Sonnengesang", "Presents"],
            "Titel_Svensk": ["Faust, en sång om solen", "Presenter"],
            "Granskningsnummer": ["1111", "2222"]
        }
    )

    matches = get_primary_key(df, "faust sonnengesang")

    assert matches == "1111"


def test_get_primary_key_not_in_registry():
    """
    Tests that the function correctly raises a ValueError if the title of the movie is not found in the registry.
    """

    df = pd.DataFrame(
        {
            "Titel_Org": ["Faust Sonnengesang"],
            "Titel_Svensk": ["Faust, en sång om solen"],
            "Granskningsnummer": ["1111"]
        }
    )

    with pytest.raises(ValueError):
        get_primary_key(df, "hello world")


def test_get_primary_key_column_not_in_registry():
    """
    Tests that the function correctly raises a KeyError if somehow a column name is used that is not found in the registry.
    """

    df = pd.DataFrame(
        {
            "Titel_Org": ["Faust Sonnengesang"],
            "Titel_Dansk": ["Faust, en sång om solen"],
            "Granskningsnummer": ["1111"]
        }
    )

    with pytest.raises(KeyError):
        get_primary_key(df, "faust sonnengesang")


def test_get_other_info_convert_to_int():
    """
    Tests that the function correctly raises a ValueError if the value for "Klipp_antal" can not be converted to an integer.
    """
    df = pd.DataFrame(
        {
            "Granskningsnummer": ["1111"],
            "Klipp_Antal": ["String"]
        }
    )

    with pytest.raises(ValueError):
        get_other_info(df, "1111")


def test_find_cuts():
    """
    Tests that the function gets the values only from movies with the given primary key, and also that it returns the values from the expected keys.
    """
    df = pd.DataFrame(
        {
            "Granskningsnummer": ["1111", "456"],
            "Bortklippt_beskrivning": ["Kattögon", "Hundögon"],
            "Motiv": ["Förråande", "Skada för barn"],
            "AAtgaerd": ["Klippt", "Utgår"]
        }
    )

    matches = find_cuts(df, "1111")

    expected = [
        {
            "Bortklippt_beskrivning": "Kattögon",
            "Motiv": "Förråande",
            "AAtgaerd": "Klippt"
        }
    ]

    assert matches == expected


def test_write_to_table():
    """
    Tests that the function correctly converts the field names.
    Does not otherwise test that the PrettyTable class from prettytables works as intended.
    """
    table = write_to_table(
        [
            {
                "Bortklippt_beskrivning": ["Kattögon"],
                "Motiv": ["Förråande"],
                "AAtgaerd": ["Klippt"]
            }
        ]
    )
    assert table.field_names == ["Beskrivning av bortklippt del",
                                 "Motivering för censur-klipp", "Beslutad åtgärd"]


def test_write_to_txt():
    """
    Tests that the function creates a new file based on the key input and that it writes out the text from the summary and table inputs.
    The function does not test the formatting of the table created earlier using PrettyTable().
    """
    key = 1111
    summary = "The movie 'Askungen', is of category animerad from 1950 produced in USA"
    table = "Test"

    write_to_txt(key, summary, table)

    assert os.path.exists("1111.txt")

    with open("1111.txt", "r") as file:
        content = file.read()

    assert content == "The movie 'Askungen', is of category animerad from 1950 produced in USA\nTest"

    os.remove("1111.txt")
