from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from .models import Threadlist
from threading import Thread, Event
import ccxt
import random
import urllib.parse
from time import sleep
import json

thread_list = []

test_g_v = 0
# Kucoin Thread
ticket_value = False


class MyThread(Thread):
    def __init__(self, min_val, max_val, interval_val, symbol_val, api_key, secret_key, password, exchange):
        super().__init__()
        self.min_val = min_val
        self.max_val = max_val
        self.interval_val = interval_val
        self.symbol_val = symbol_val
        self.api_key = api_key
        self.secret_key = secret_key
        self.password = password
        self.exchange = exchange
        self.remain = 0
        self._stop_event = Event()
        self.th_index = len(thread_list)

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            try:
                e_rate = self.exchange.fetch_ticker(self.symbol_val)
                rand_amount = random.randint(
                    int(self.min_val), int(self.max_val))
                sell_amount = rand_amount / e_rate['close']

                self.exchange.create_order(
                    self.symbol_val, 'market', 'sell', 0.01)
                global test_g_v
                test_g_v += 1
                balance = self.exchange.fetch_balance()

                remaining_eth = balance[self.symbol_val.split("/")[0]]['free']
                if remaining_eth < 0.05:
                    # if remaining_eth < (self.max_val / e_rate['close'])*2:
                    self._stop_event.set()
                    thread_list.pop(self.th_index)
                    Threadlist.objects.filter(
                        api_key=self.api_key).delete()
                    return

                self.remain = remaining_eth
                Threadlist.objects.filter(
                    api_key=self.api_key).update(crypto_remain=str(remaining_eth))

                print("Remaining ETH", self.th_index, ":", remaining_eth)

            except:
                self._stop_event.set()
                thread_list.pop(self.th_index)
                print(len(thread_list))
                global ticket_value
                ticket_value = True
                return

            sleep(int(self.interval_val))
# define System Thread


def set_exchange(api_key, secret_key, password):
    exchange = ccxt.kucoin({
        'apiKey': api_key,
        'secret': secret_key,
        'password': password,
        'enableRateLimit': True,
    })

    exchange.set_sandbox_mode(True)

    return exchange


def init_thread():
    if len(Threadlist.objects.all().values()) == 0:
        return
    for i in Threadlist.objects.all().values():
        exchange = set_exchange(i['api_key'], i['secret_key'], i['password'])
        new_thread = MyThread(api_key=i['api_key'], secret_key=i['secret_key'], password=i['password'],
                              min_val=i['min_val'], max_val=i['max_val'], interval_val=i['interval_time'],
                              symbol_val=i['marketing_symbol'], exchange=exchange)

        thread_list.append(new_thread)
        thread_list[-1].start()


init_thread()


class SystemThread(Thread):
    def __init__(self):
        super().__init__()
        self._stop_event = Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            if len(Threadlist.objects.all().values()) > len(thread_list):
                for s_thread in thread_list:
                    s_thread.stop()
                thread_list.clear()
                init_thread()
            sleep(15)


syst = SystemThread()
# syst.start()

# return the ccxt exchange


# init thread


# return the main view


def index(request):

    context = {"selling_process": Threadlist.objects.all()}

    return render(request, "mainbot/index.html", context)

# register the thread


def register(request):

    ss = request.body
    input_string = ss.decode("utf-8")

    ss = urllib.parse.parse_qs(input_string)

    for key in ss:
        ss[key] = ss[key][0]

    exchange = set_exchange(
        ss['api_key'], ss['secret_key'], ss['api_password'])

    try:
        exchange.fetch_balance()
        print(exchange)
    except:
        return HttpResponse("incorrect")

    if Threadlist.objects.filter(api_key=ss['api_key']).exists():
        return HttpResponse("repeat")

    new_thread = MyThread(api_key=ss['api_key'], secret_key=ss['secret_key'], password=ss['api_password'],
                          min_val=ss['min_val'], max_val=ss['max_val'], interval_val=ss['interval_time'],
                          symbol_val=ss['marketing_symbol'], exchange=exchange)

    thread_list.append(new_thread)
    thread_list[-1].start()

    new_record = Threadlist(api_key=ss['api_key'], secret_key=ss['secret_key'], password=ss['api_password'],
                            min_val=ss['min_val'], max_val=ss['max_val'], interval_time=ss['interval_time'],
                            marketing_symbol=ss['marketing_symbol'], crypto_remain="0")
    new_record.save()

    return HttpResponse("success")

# reset all data


def stopporcess(request):

    for s_thread in thread_list:
        s_thread.stop()

    Threadlist.objects.all().delete()
    thread_list.clear()

    return HttpResponse("success")


def test(request):

    print(len(thread_list))

    return JsonResponse({'a': test_g_v, 'b': len(thread_list)})


def getremain(request):
    remain_data = Threadlist.objects.all().values()
    if len(remain_data) == 0:
        return HttpResponse('dsfsd')

    return JsonResponse({'foo': list(remain_data)})
