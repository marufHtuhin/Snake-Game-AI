import asyncio
import pygame
from settings import WIDTH, HEIGHT, FPS, TITLE
from game import SnakeGame


async def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    game = SnakeGame(screen)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        running = game.handle_events()
        game.update(dt)
        game.draw()
        pygame.display.flip()
        await asyncio.sleep(0)  # required for browser (WebAssembly) builds

    pygame.quit()


asyncio.run(main())
