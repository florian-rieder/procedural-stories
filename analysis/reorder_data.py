import pandas as pd
import os


def read_model_order(channel: str) -> str:
    """
    Reads the model order (A/B or B/A) from the channel's model_order.txt file.

    Args:
        channel: The discord channel number

    Returns:
        str: The model order ("A/B" or "B/A")
    """
    try:
        with open(f"data/{channel}/model_order.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def reorder_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reorders values between first and second system responses if order is B/A.
    Also swaps preference responses accordingly.
    Should be called with a single-row DataFrame.

    Args:
        df: The input dataframe (single row)

    Returns:
        pd.DataFrame: DataFrame with potentially swapped values
    """
    if len(df) != 1:
        raise ValueError("reorder_columns expects a single-row DataFrame")

    # Get the channel number from the "Numéro de channel discord" column
    channel = str(df["Numéro de channel discord"].iloc[0])
    order = read_model_order(channel)

    print(f"\nProcessing channel {channel} with order {order}")

    if not order:
        return df

    # Create a copy to avoid modifying the original
    result = df.copy()

    if order == "B/A":
        # Store the values temporarily
        temp_values = result.iloc[0, 8:36].copy()
        # Copy second system values to first position
        result.iloc[0, 8:36] = result.iloc[0, 36:64].values
        # Copy stored first system values to second position
        result.iloc[0, 36:64] = temp_values.values

        # Swap preference responses
        preference = result["Globalement, j'ai préféré"].iloc[0]
        if preference == "Le système A":
            result["Globalement, j'ai préféré"].iloc[0] = "Le système B"
        elif preference == "Le système B":
            result["Globalement, j'ai préféré"].iloc[0] = "Le système A"

    return result


def main():
    """
    Main function to process the raw results file.
    """
    # Read the CSV file with | as delimiter
    df = pd.read_csv("data/raw_results.csv", sep=",", header=0)

    # Then process each row for reordering
    results = []
    for _, row in df.iterrows():
        results.append(reorder_columns(pd.DataFrame([row])))

    # Combine all results
    final_df = pd.concat(results)

    # Save to new CSV
    final_df.to_csv("data/processed_results.csv", sep=",", index=False)


if __name__ == "__main__":
    main()
