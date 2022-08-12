# Ready Or Not ?

A local-multiplayer RPG action game built using [python-arcade](https://github.com/pythonarcade/arcade). 
Map designed using [Tiled Map Editor](https://www.mapeditor.org/)

#### Watch the gameplay 👉 [Ready or Not](https://youtu.be/3jix7ebgA_s)


![Home screen](https://github.com/mochatek/ReadyOrNot/blob/master/res/screen.png)


## Game Instructions

- Two teams (**Guards & Thieves**) can compete in a match.

- Team can be **Duo** (2 players) or **Squad** (4 players).

- Start the game **Server** and choose the **Mode** (Duo/Squad).

- **Rooms** will be of different colors. You need to have **Swipe Card** matching the color of the room in order to access it's **Door**.

- **Loots**, weapons (Pistol & Knife) and swipe cards can be found on the floor.

- **Pistol** deal low damage but have high range. For **Knife**, it's vice versa.

- You can **Restore Health** using medicine from the **FAB** (Medicine is limited, so use wisely).

- When you knock down an opponent, he will loose all his loots and get **Locked up** in your **Prison**. You can collect his loot.

- Teammates can **Rescue** locked up players, provided they have swipe card of that prison.

- You can toggle (On/Off) the **Electricity** using the **Main Switch** to play out your strategy.

- Thieves try to steal items, whereas guards try to prevent it.

- Team which have either **(2 * mode) loots** or **(mode / 2) opponents in prison** will be declared the **Winner**.

- **`So, are you Ready or Not ❓`**


## Installation

- Download and Install [Python3](https://www.python.org/downloads/)

- It is recommended to use a virtual environment

- Once virtual environment is set up, use [pip](https://pip.pypa.io/en/stable/reference/pip_download/) to install the dependencies by running the command

```
pip install -r requirements.txt
```


## How to Run

- Start the server using the command `python server.py`

- Launch the game using the command `python client.py`

- You can otherwise create an `exe` for server and client using [pyinstaller](https://www.pyinstaller.org/), and run directly.

⚠️ **_If you encounter any errors, do the workarounds specified in the beginning of `client.py` file_**


## Controls and Credits

![Controls](https://github.com/mochatek/ReadyOrNot/blob/master/res/info.png)


## Contributing

Pull requests are welcome.
For major changes, please open an issue first to discuss what you would like to change.


## License

[MIT](https://github.com/mochatek/ReadyOrNot/blob/master/LICENSE)
