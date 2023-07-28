import json
import time
from rich.console import Console
import matplotlib.pyplot as plt

class Data:
    def __init__(self):
        self.max_bet = [0, 0, 0]
        self.house_profit = 0
        self.house_profit_by_rounds = []
        self.list_rounds = [] # [[count,red bet,green bet,black bet,winner],...]
        self.win_lose_list = []
        self.most_consecutive_loss = 0
        self.most_consecutive_wins = 0

    @classmethod
    def cprint(cls, text):
        color, total = 'white', 0.3
        console = Console()
        delay = total / len(text)
        for char in text:
            if char == '.':
                console.print(char, style='bold magenta', end="")
            else:
                console.print(char, style=color, end="")
            time.sleep(delay)
        console.print()

    @classmethod
    def output_stream(cls, string):
        file = open('data.txt', 'a')
        file.write(string)

    def scatter_chart(self, x_values, y_values, x_label, y_label, title):
        plt.scatter(x_values, y_values)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.show()

    def line_chart(self, x_values, y_values, x_label, y_label, title):
        plt.plot(x_values, y_values)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.show()

    def graph_house_profit_by_rounds(self):
        points = self.house_profit_by_rounds
        x_values = [(i + 1) for i in range(len(points))]
        y_values = [points[i] for i in range(len(points))]
        self.scatter_chart(x_values, y_values, 'rounds', 'profit', 'House Profit by Rounds')

    def graph_total_house_profit(self):
        points = self.house_profit_by_rounds
        x_values = [(i + 1) for i in range(len(points))]
        cur, y_values = 0, []
        for point in points:
            cur += point
            y_values.append(cur)
        self.line_chart(x_values, y_values, 'rounds', 'profit', 'House Total Profit Chart')

    def graph_win_lose_ratio(self):
        points = self.house_profit_by_rounds
        x_values = [(i + 1) for i in range(len(points))]
        y_values = []
        position = 0
        for point in points:
            if point > 0:
                position += 1
                y_values.append(position)
            elif point < 0:
                position -= 1
                y_values.append(position)
            else:
                y_values.append(position)
            self.win_lose_list.append(position)
  
        self.line_chart(x_values, y_values, 'rounds', 'win/lose', 'win/lose ratio')
    
    def get_consecutive_wins_losses(self):
        if len(self.win_lose_list) == 0:
            print("Execute graph_win_lose_ratio method first")
            return
        lst = self.win_lose_list

        win_streak, lose_streak = 0, 0
        for i in range(len(lst)):  # Corrected the loop starting index
            if i > 0 and (lst[i - 1] + 1) == lst[i]:  # Check for consecutive win
                lose_streak = 0
                win_streak += 1
                self.most_consecutive_wins = max(self.most_consecutive_wins, win_streak)
            elif i > 0 and (lst[i - 1] - 1) == lst[i]:  # Check for consecutive loss
                win_streak = 0
                lose_streak += 1
                self.most_consecutive_loss = max(self.most_consecutive_loss, lose_streak)

        print(f'The most consecutive wins are {self.most_consecutive_wins}\nThe most consecutive losses are {self.most_consecutive_loss}')
     
    def initialize_data_analysis(self):
        with open('data.txt', 'r') as file:
            # [[count,red,green,black,winner],...]
            list_of_rounds = file.readlines() 
            list_of_rounds = [round.replace('\n', '').split(',') for round in list_of_rounds]
            self.list_rounds = list_of_rounds

            for i, round in enumerate(list_of_rounds):
                if i == 0: continue
        
                round_house_profit = float(round[1]) + float(round[2]) + float(round[3])
                if round[4] == 'BLACK':
                    round_house_profit -= (float(round[3]) * 2)
                elif round[4] == 'GREEN':
                    round_house_profit -= (float(round[2]) * 14)
                elif round[4] == 'RED':
                    round_house_profit -= (float(round[1]) * 2)

                self.house_profit_by_rounds.append(round_house_profit)
                self.house_profit += round_house_profit

                self.max_bet = [
                    max(self.max_bet[0], float(round[1])),
                    max(self.max_bet[1], float(round[2])),
                    max(self.max_bet[2], float(round[3]))
                ]
            
            if int(self.house_profit) != int(sum(self.house_profit_by_rounds)):
                raise ValueError
            else:
                self.cprint('Data analysis success!')
    
    def algorithm_data_test(self):
        number_of_correct_guesses = 0
        total_risks = 0
        for i, round in enumerate(self.list_rounds):
            if i == 0: continue
            red_bet = float(round[1])
            green_bet = float(round[2])
            black_bet = float(round[3])
            # restrictions: only bet if there are two non-zero bets!
            num_zero_bets = 0
            if red_bet == 0:
                num_zero_bets += 1
            if green_bet == 0:
                num_zero_bets += 1
            if black_bet == 0:
                num_zero_bets += 1

            if num_zero_bets >= 3:  # if there are two untaken spots, don't take it
                continue #(red_bet + green_bet + black_bet) <= 2:

            total_risks += 1

            if (red_bet < ((green_bet * 13) + black_bet)) and (round[4] == 'RED'):
                number_of_correct_guesses += 1
            elif ((green_bet * 13) < (red_bet + black_bet)) and (round[4] == 'GREEN'):
                number_of_correct_guesses += 1
            elif (black_bet < ((green_bet * 13) + red_bet))  and (round[4] == 'BLACK'):
                number_of_correct_guesses += 1

        self.cprint(f'The number of correct guesses are {number_of_correct_guesses} out of {total_risks}')
        self.cprint(f'If you bet 1 WL, you will earn {number_of_correct_guesses - (total_risks - number_of_correct_guesses)} WLS.')
        self.cprint(f'The success rate is {(number_of_correct_guesses) / (total_risks) * 100} %\n')

    # [None,red bet,green bet,black bet,None]
    def algorithm_execution(self, round):
        red_bet = float(round[1])
        green_bet = float(round[2])
        black_bet = float(round[3])

        # restrictions: only bet if there are two non-zero bets!
        num_zero_bets = 0
        if red_bet == 0:
            num_zero_bets += 1
        if green_bet == 0:
            num_zero_bets += 1
        if black_bet == 0:
            num_zero_bets += 1

        if num_zero_bets >= 3:  # if there are two untaken spots, don't take it
            return # (red_bet + green_bet + black_bet) <= 2:

        if (red_bet < ((green_bet * 13) + black_bet)):
            print(f'{red_bet} {green_bet} {black_bet}')
            print("Betting on RED!")
            return 'RED'
        elif ((green_bet * 13) < (red_bet + black_bet)):
            print(f'{red_bet} {green_bet} {black_bet}')
            print("Betting on GREEN!")
            return 'GREEN'
        elif (black_bet < ((green_bet * 13) + red_bet)):
            print(f'{red_bet} {green_bet} {black_bet}')
            print('Betting on BLACK!')
            return 'BLACK'
