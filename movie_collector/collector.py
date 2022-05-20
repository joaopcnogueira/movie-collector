import os
import requests
import pandas as pd
from tqdm import tqdm
from dotenv import dotenv_values

THIS_FILE = os.path.abspath(__file__)
WORK_DIR = os.path.dirname(os.path.dirname(THIS_FILE))
DATA_DIR = os.path.join(WORK_DIR, "data")

config = dotenv_values(".env")


class MovieCollector:
    """
    Downloads data from The Movie Database:
    https://www.themoviedb.org/documentation/api
    """

    def __init__(self, api_key, download_new):
        """
        Parameters
        ----------
        api_key : the api key need to query the movie database api

        download_new : bool, determines whether new data will be downloaded
        or whether local saved data will be used
        """
        self.api_key = api_key
        self.download_new = download_new

    def fetch_data(self):
        """
        Fetch the data from the movie db api

        Returns
        -------
        DataFrame
        """
        response_list = []
        for movie_id in tqdm(range(1, 1001)):
            url = (f"https://api.themoviedb.org/3/"
                   f"movie/{movie_id}?api_key={self.api_key}")
            r = requests.get(url)
            response_list.append(r.json())

        return pd.DataFrame.from_dict(response_list)

    def write_data(self, df, output_name, dir, **kwargs):
        """
        Writes data DataFrame to a file as a CSV

        Parameters
        ----------
        df : pandas DataFrame

        output_name: string name of the output file

        dir : string name of directory to save files within data directory,
        i.e. "raw" or "prepared"

        Returns
        -------
        None
        """
        df.to_csv(os.path.join(DATA_DIR, f"{dir}/{output_name}.csv"), **kwargs)

    def select_columns(self, df):
        """
        Select columns

        Parameters
        ----------
        df : pandas DataFrame

        Returns
        -------
        DataFrame
        """
        columns_to_select = ['id',
                             'imdb_id',
                             'original_title',
                             'release_date',
                             'runtime',
                             'revenue',
                             'genres']
        return df.filter(columns_to_select)

    def extract_genres(self, df):
        """
        Extract genres into columns, by exploding them

        Parameters
        ----------
        df : pandas DataFrame

        Returns
        -------
        DataFrame
        """
        df = df.dropna()
        genres_series = df['genres'].apply(lambda lista: '|'.join([
            elemento['name'] for elemento in lista
        ]))
        genres_df = genres_series.str.get_dummies("|")
        genres_df['qtd_genres'] = genres_df.sum(axis="columns")
        genres_df.columns = genres_df.columns.str.lower()
        df = df.drop('genres', axis=1).join(genres_df)
        return df

    def build_datetime_features(self, df):
        """
        Build datetime features

        Parameters
        ----------
        df : pandas DataFrame

        Returns
        -------
        DataFrame
        """
        df['release_date'] = pd.to_datetime(df['release_date'])
        df['day'] = df['release_date'].dt.day
        df['month'] = df['release_date'].dt.month
        df['year'] = df['release_date'].dt.year
        df['day_of_week'] = df['release_date'].dt.day_name()
        return df

    def run(self):
        """
        Run all downloading, cleaning and transformation steps

        Returns
        -------
        DataFrame
        """
        if self.download_new:
            df = self.fetch_data()
            self.write_data(df, output_name="imdb_raw", dir="raw", index=False)
            df = self.select_columns(df)
            df = self.extract_genres(df)
            df = self.build_datetime_features(df)
            self.write_data(df, output_name="imdb_prepared", dir="prepared",
                            index=False)
            return df
        else:
            # return pd.read_csv("data/prepared/imdb_prepared.csv")
            return pd.read_csv(os.path.join(DATA_DIR, "prepared/imdb_prepared.csv"))


if __name__ == "__main__":
    collector = MovieCollector(api_key=config["API_KEY"], download_new=True)
    df = collector.run()
