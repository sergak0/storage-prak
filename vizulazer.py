import json
import random
import time

import pandas as pd
import pygame as pg
from pygame.math import Vector2

product_names = ["egg", "fish", 'meat', 'apple', 'pear', 'milk', 'water', 'bread', 'cake',
                 'napkins', 'soap', 'shampoo', 'coal', 'beer', 'porrige', 'apple juice',
                 'cherry juice', 'crakers', 'domestos', 'tomato']


class MySprite(pg.sprite.Sprite):
    def __init__(self, pos, goal, image, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.vel = Vector2(0, 0)
        self.pos = Vector2(pos)
        self.max_speed = 10
        self.goal = Vector2(goal)
        self.goal_radius = 40

    def update(self):
        self.pos += self.vel
        self.rect.center = self.pos

        heading = self.goal - self.pos
        distance = heading.length()
        if heading:
            heading.normalize_ip()

        if distance > self.goal_radius:
            self.vel = heading * self.max_speed
        else:
            self.vel = heading * (distance/self.goal_radius * self.max_speed)

    def is_ready(self):
        return self.vel.length() < 1


class ShopsCoordinates:
    def __init__(self, step_goal, size):
        self.step_goal = step_goal
        self.n = 7
        self.size = size

    def get_goal(self, number):
        x = number // self.n % 4
        y = number // self.n // 4
        if x == 0:
            return Vector2(number % self.n * self.step_goal + self.step_goal * 2,
                           y * self.step_goal + self.step_goal)
        elif x == 1:
            return Vector2(self.size - y * self.step_goal - self.step_goal,
                           number % self.n * self.step_goal + self.step_goal * 2)
        elif x == 2:
            return Vector2(self.size - number % self.n * self.step_goal - self.step_goal * 2,
                           self.size - y * self.step_goal - self.step_goal)
        else:
            return Vector2(y * self.step_goal + self.step_goal,
                           self.size - number % self.n * self.step_goal - self.step_goal * 2)


class DataGen:
    def __init__(self, data, shops_count):
        self.data = data
        self.shops_count = shops_count
        self.cnt_send = 0
        self.new_product_step = 3
        self.cnt_updated = 0
        self.product_ind = 0
        self.day = 0

    def get(self):
        self.cnt_updated += 1
        if self.cnt_updated % self.new_product_step != 0:
            return []

        res = []
        today = self.data[self.data['day'] == self.day]
        while self.product_ind < len(product_names) and len(today[today[product_names[self.product_ind]] != 0]) == 0:
            self.product_ind += 1

        if self.product_ind == len(product_names):
            return []

        name = product_names[self.product_ind]
        for i in range(self.shops_count):
            if (today['shop_id'] == i).sum() == 0:
                continue

            sends_products = today[today['shop_id'] == i][name].values[0]
            if sends_products > self.cnt_send:
                res.append((i, name))
        self.cnt_send += 1

        if len(res) == 0:
            self.product_ind += 1
            self.cnt_send = 0

        return res

    def new_day(self):
        self.cnt_send = 0
        self.product_ind = 0
        self.cnt_updated = 0
        if self.day < self.data['day'].max():
            self.day += 1
        else:
            self.day = 0


class App:
    colors = {name: (random.randint(40, 255), random.randint(40, 255), random.randint(40, 255)) for name in product_names}

    def __init__(self, shops_count, data):
        self.font = pg.font.SysFont('Comic Sans MS', 20)
        self.day_number_font = pg.font.SysFont('Comic Sans MS', 30)
        self.start_pos = Vector2(250, 250)
        self.all_sprites = pg.sprite.Group()
        self.screen = pg.display.set_mode((750, 500))
        self.clock = pg.time.Clock()
        self.shops_count = shops_count
        self.draw_texts = False

        self.shops_coord = ShopsCoordinates(50, 500)
        self.data_gen = DataGen(data, shops_count)

        shop_sprite = pg.Surface((30, 30))
        shop_sprite.fill(pg.Color('dodgerblue1'))
        self.shops = [MySprite(self.start_pos, self.shops_coord.get_goal(i), shop_sprite, self.all_sprites) for i in range(shops_count)]

        self.products = []

    def get_product_image(self, name):
        now = pg.Surface((10, 10))
        now.fill(self.colors[name])
        return now

    def show_product_names(self):
        for i, name in enumerate(product_names):
            textsurface = self.font.render(name, False, self.colors[name])
            if i > 10:
                goal = Vector2(620, 20 + (i - 10) * 30)
            else:
                goal = Vector2(520, 20 + i * 30)

            if self.draw_texts is False:
                now_img = self.get_product_image(name)
                MySprite(self.start_pos, goal - Vector2(10, -17), now_img, self.all_sprites)
            self.screen.blit(textsurface, goal)

        textsurface = self.day_number_font.render('Today: {}'.format(self.data_gen.day), False, pg.Color('dodgerblue1'))
        self.screen.blit(textsurface, (550, 400))

        try:
            now_product = product_names[self.data_gen.product_ind]
            textsurface = self.day_number_font.render(now_product, False, self.colors[now_product])
            self.screen.blit(textsurface, (552, 450))
        except:
            now_product = ""

        self.draw_texts = True

    def update_cars(self):
        ready = True
        for product in self.products:
            ready = min(product.is_ready(), ready)

        if ready and len(self.products):
            for i in range(len(self.products)):
                self.products[i].kill()

            self.data_gen.new_day()
            print('new day)')
            self.products = []

        sended_product = self.data_gen.get()
        for shop_id, name in sended_product:
            self.products.append(MySprite(self.start_pos,
                                          self.shops_coord.get_goal(shop_id),
                                          self.get_product_image(name),
                                          self.all_sprites))

    def run(self):
        done = False
        while not done:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    done = True

            self.update_cars()
            self.all_sprites.update()
            self.screen.fill((30, 30, 30))
            self.show_product_names()
            self.all_sprites.draw(self.screen)

            pg.display.flip()
            self.clock.tick(30)


if __name__ == '__main__':
    pg.init()
    pg.font.init()
    data = pd.read_csv('data_shops.csv')
    for name in product_names:
        if not name in data.columns:
            data[name] = 0

    shops_cnt = data['shop_id'].max() + 1
    app = App(shops_cnt, data)
    app.run()
    pg.quit()

