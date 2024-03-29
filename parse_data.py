import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import re
from datetime import datetime
import datetime as dt


def main():
    # open text file
    with open('swiggy_data.txt') as file:
        # load json data
        order_data = json.load(file)

        # print_all_orders(order_data)

        # getting number of orders
        num_orders = len(order_data)

        # getting price details
        net_price, gross_price, price_list = get_total_price(order_data)

        # getting basic price statistics
        average_order_value = np.mean(price_list)
        median_order_value = np.median(price_list)
        std_order_value = np.std(price_list)

        plot_price_distribution(price_list)

        # getting restaurant and item statistics
        restaurant_freq, item_freq = get_item_and_restaurant_data(order_data)
        # sorting by most frequented
        restaurant_freq = restaurant_freq.sort_values(
            by='Frequency', ascending=False)
        item_freq = item_freq.sort_values(by='Frequency', ascending=False)

        # number of restaurants and items tried
        rest_tried = restaurant_freq.shape[0]
        items_tried = item_freq.shape[0]

        print(f'Number of restaurants tried:{rest_tried}')
        print(f'Number of items tried:{items_tried}')
        print(restaurant_freq.head(15))
        print(item_freq.head(15))

        print(f'Average order value:{average_order_value}')
        print(f'Median order value:{median_order_value}')
        print(f'Std order value:{std_order_value}')

        date_data = get_timeline_data(order_data)
        plot_date_distribution(date_data)


def get_total_price(order_data):
    total_gross_price = 0
    total_net_price = 0
    net_price_list = []

    # iterating over all orders and adding up prices
    for order in order_data:

        # pre discounts
        restaurant_bill = float(order['order_restaurant_bill'])
        delivery_charges = float(
            order['order_delivery_charge'])
        gross_price = restaurant_bill + delivery_charges

        # post discounts
        net_price = order['order_total']

        # update prices
        total_gross_price += gross_price
        total_net_price += net_price
        net_price_list.append(net_price)

    return total_net_price, total_gross_price, net_price_list


def get_timeline_data(order_data):
    date_list = []
    for order in order_data:
        date_time = order['order_time']
        # extracting datetime object from string
        match = re.search(r'\d{4}-\d{2}-\d{2}', date_time)
        date = datetime.strptime(match.group(), '%Y-%m-%d').date()
        date_list.append(date.strftime('%B-%Y'))
    return date_list


def plot_price_distribution(price_list):
    num_bins = 48
    n, bins, patches = plt.hist(price_list, num_bins)
    plt.title('Distribution of order value')
    plt.xlabel('Order value (₹)')
    plt.ylabel('Number of orders')
    plt.show()


def plot_date_distribution(date_list):
    year_list = []
    freq_table = dict()
    ticklabels = [dt.date(1900, i, 1).strftime('%b')
                  for i in range(1, 13)]
    # getting all years involved
    for date in date_list:
        year = datetime.strptime(date, '%B-%Y').date().year
        if year not in year_list:
            year_list.append(year)
    year_list.sort()

    # creating year table
    for year in year_list:
        months = [0 for i in range(1, 13)]
        freq_table[year] = months

    # populating year table
    for date in date_list:
        year = datetime.strptime(date, '%B-%Y').date().year
        month = datetime.strptime(date, '%B-%Y').date().month
        # updating year table
        freq_table[year][month-1] += 1

    colors = ['#c41f21', '#f64d4a', '#fb5e4e', '#fd7f5d',  '#fdaf87']
    # plotting year table
    fig, plots = plt.subplots()
    for year in year_list:
        x_data = [month for month in range(1, 13)]
        y_data = [year for i in range(12)]
        plots.scatter(x_data, y_data, s=np.array(
            freq_table[year])*50, alpha=0.5,  c=colors[year-year_list[0]])
    plt.title('Number of orders with time')
    plt.yticks(year_list)
    plots.set_xticks([i for i in range(1, 13)])
    plots.set_xticklabels(ticklabels)
    plt.show()

    return year_list


def get_item_and_restaurant_data(order_data):
    restaurant_freq = dict()
    item_freq = dict()
    # iterate over all orders
    for order in order_data:
        # get and item data
        restaurant = order['restaurant_name']
        item_list = order['order_items']

        # get number of times ordered
        if restaurant not in restaurant_freq:
            restaurant_freq[restaurant] = 1
        else:
            restaurant_freq[restaurant] += 1

        # get item details and quantity
        for item in item_list:
            item_name = item['name']
            quantity = int(item['quantity'])

            if item_name not in item_freq:
                item_freq[item_name] = quantity
            else:
                item_freq[item_name] += quantity

    # converting to pandas dataframe for ease of manipulation
    rest_list = [(rest, freq) for rest, freq in restaurant_freq.items()]
    rest_names = [entry[0] for entry in rest_list]
    rest_freq = [entry[1] for entry in rest_list]
    restaurant_data = {'Restaurant': rest_names, 'Frequency': rest_freq}
    restaurant_dataframe = pd.DataFrame.from_dict(restaurant_data)

    item_list = [(item, freq) for item, freq in item_freq.items()]
    item_names = [entry[0] for entry in item_list]
    item_freq = [entry[1] for entry in item_list]
    item_data = {'Item': item_names, 'Frequency': item_freq}
    item_dataframe = pd.DataFrame.from_dict(item_data)

    return restaurant_dataframe, item_dataframe


def print_all_orders(order_data):
    # iterate through data for each order
    for index, order in enumerate(order_data):

        order_id = order['order_id']

        # date and time of order
        date_time = order['order_time']
        print(date_time)

        # Name of restaurant
        restaurant = order['restaurant_name']
        print(f'Restaurant:{restaurant}')

        # list containing all items in order
        item_list = order['order_items']

        # individual items and their quantities
        for item in item_list:
            item_name = item['name']
            quantity = item['quantity']
            print(f'{item_name} x {quantity}')

        # getting final price of item
        price = order['net_total']
        print(f'₹{price}')
        print('')


if __name__ == '__main__':
    main()
