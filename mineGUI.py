import random
from tkinter import *
from tkinter import simpledialog, messagebox
import time

class Cell:
    """Cell is a container for each cell of a minesweeper game"""
    def __init__(self, row, col, isHidden = True, isMine = False, isFlag = False):
        self.isHidden = isHidden
        self.row = row
        self.col = col
        self.isMine = isMine
        self.isFlag = isFlag
        
    def doHide(self):
        self.isHidden = True
    
    def unHide(self):
        self.isHidden = False
        self.isFlag = False  # Being Conservative!
        
    def flag(self):
        if self.isHidden: # flag on a revealed cell is strange!
            self.isFlag = True
        else:
            raise ValueError("Flag on revealed cell!") #  TODO: Do I need this?
        
    def toggle_flag(self):
        if self.isHidden:
            self.isFlag = not self.isFlag
        else:
            raise ValueError("Flag on revealed cell!")

    def unflag(self):
        self.isFlag = False
        
        
class Board:
    """Board is a class for managing the board of the minesweeper game"""
    def __init__(self, N , num_mines):
        """ initializes a (@N x @N) board of Cells and adds @num_mines mines to the board """
        self.N = N
        self.reveal_count = 0
        self.num_mines = num_mines
        #initializing the board
        self.board = [[Cell(row,col) for row in range(N)] for col in range(N)]
        assert( num_mines <= N**2), "Number of mines must not be greater than the number of cells!" #TODO: change it to raise?
        self.mine_counter = {}
        for i in range(num_mines):
            r = random.randrange(0,N)
            c = random.randrange(0,N)
            
            while self.board[r][c].isMine:
                r = random.randrange(0,N)
                c = random.randrange(0,N)
                
            self.board[r][c].isMine = True
            
    def print_board(self, show_mines = False):
        for r in range(self.N):
            for c in range(self.N):
                print(self.get_board_element(r,c, show_mines),end='')
            print('')


    def get_board_elements(self, show_mines = False):
        cells = []
        for i in range(self.N):
                cells.append([])
        for r in range(self.N):
            for c in range(self.N):
                cells[r].append( self.get_board_element(r,c, show_mines))
        return cells

    def get_board_element(self, row, col, show_mines = False):
        self.check_row_col_raise(row,col)
        aCell = self.board[row][col]
        if aCell.isMine and show_mines:
            return '@'
        elif not aCell.isHidden:
            return str(self.count_mines(row,col))
        elif aCell.isFlag:
            return 'P'
        else:
            return '#'
            
    def check_row_col(self, row, col):
        if row < 0 or row >= self.N or col < 0 or col >= self.N:
            return False
        return True
    
    def check_row_col_raise(self,row,col):
        if not self.check_row_col(row,col):
            error = IndexError("You are attemping a bad index in the board!")
            raise error

    def put_flag(self, row, col):
        self.check_row_col_raise(row,col)
        self.board[row][col].flag()
            
    def remove_flag(self, row, col):
        self.check_row_col_raise(row,col)
        self.board[row][col].unflag()

    def toggle_flag(self, row, col):
        self.check_row_col_raise(row,col)
        self.board[row][col].toggle_flag()
        
    def count_mines(self, row, col):
        self.check_row_col_raise(row,col)
        if not self.mine_counter.get((row,col)) == None:
            return self.mine_counter[(row,col)]
        # Assuming current row,col is not a mine. the behaviour is not clarified, though
        # This must be only called from reveal_cell (i.e., private method)
        mine_count = 0
        for c in range(col-1,col+2):
            for r in range(row-1,row+2):
                if self.check_row_col(r,c):
                    if self.board[r][c].isMine:
                        mine_count += 1
                        
        self.mine_counter[(row,col)] = mine_count
        return mine_count
    
    def reveal_cell(self, row, col):
        self.check_row_col_raise(row,col)
        if self.board[row][col].isMine:
            return -1
        if self.board[row][col].isFlag:
            return -2
        mine_count = self.count_mines(row,col)
        if self.board[row][col].isHidden:
            self.board[row][col].unHide()
            #Mosbati
            if mine_count == 0:
                for c in range(col-1,col+2):
                    for r in range(row-1,row+2):
                        if self.check_row_col(r,c) and self.board[r][c].isHidden:
                            self.reveal_cell(r,c)
                        
            self.reveal_count += 1
        return mine_count
    
    def won(self):
        return self.N**2 - self.num_mines == self.reveal_count
    
    
class App:
    
    """ Application Manager class.
	Attributes:
		* app_type: type of application. It can be:
			- text: for the commandline application
			- test: for testing purposes ( runs a sequence of given commands )
			- gui:  for graphical user interface application

		* showWhy:  if True shows why a command is invalid.

		* isQuit:   becomes True if the user invokes quit command

		* lost:     becomes True when the user reveals a mine.

		* idx:      index of current command int test mode.

		* board:    instance of Board class.
    """
    def __init__(self, app_type = 'text', showWhy = False,**kwargs):
        """
		kwargs are mostly used in test mode.
		They must be N and num_mines.
	"""
        self.app_type = app_type
        N, num_mines = self.getN_NumMines(**kwargs)
        self.board = Board(N, num_mines)
        self.isQuit = False
        self.lost = False
        self.showWhy = showWhy
        self.idx = 0
        if app_type == 'gui':
            self.init_gui(**kwargs)


    def init_gui(self,**kwargs):
            self.master = kwargs['master']
            self.master.title('Minesweeper')
            self.master.minsize(self.board.N*30, self.board.N*30)
            self.frame = Frame(self.master)
            self.frame.grid(padx=30, pady=30)
            self.cells = []
            self.isStarted = False
            self.colors = ['lightred','darkblue','darkgreen','darkred', 'blue', 'green', 'red', 'lightblue','lightgreen']

            for i in range(self.board.N):
                self.cells.append([])

            for i in range(self.board.N):
                for j in range(self.board.N):
                    button = Button(self.frame, text='     ', bg='#DDDDDD')
                    button.config(anchor=CENTER)
                    button.grid(row=i, column=j, sticky='nswe')
                    self.cells[i].append(button)

                    def left_click_handler( event, row = i, col = j):
                        self.left_click( row, col)

                    def right_click_handler( event, row = i, col = j):
                        self.right_click( row, col)

                    button.bind('<Button-3>', right_click_handler)
                    button.bind('<Button-1>', left_click_handler)

            self.remainings = Label(self.frame, text='Mines: ')
            self.remainings.grid( row = self.board.N+1, column=1, columnspan=2, pady = 10)

            self.mines_label = Label(self.frame, text = self.board.num_mines)
            self.mines_label.grid(row = self.board.N+1, column=3, pady=0)

            self.timer = Label(self.frame, text='Time :')
            self.timer.grid(row = self.board.N+2, column=1, columnspan=2, pady=0)

            self.time_label = Label(self.frame, text='0')
            self.time_label.grid( row = self.board.N+2, column=3, pady=0)
            self.master.update()
            self.master.deiconify()

    def tick(self):
	    self.time_label.after(1000, self.tick)
	    t = int(self.time_label["text"])
	    t += 1
	    self.time_label["text"] = str(t)
	    #self.time_label.after(1000, self.tick)


    def left_click(self,row, col):
            if not self.isStarted:
                    self.isStarted = True
                    self.tick()
            print(row,col)
            try:
                x = self.board.reveal_cell(row, col)
                if x == -1:
                    self.cells[row][col]["bg"]='red'
                    self.update_all(True)
                    messagebox.showinfo('Minesweeper','You Lost!')
                    self.master.destroy()
                elif x > 0:
                    self.cells[row][col]["text"] = str(x)
                    self.cells[row][col]["fg"] = self.colors[x]
                elif x==0:
                    self.update_all()
                    pass #TODO zero, update all
                if self.board.won():
                    messagebox.showinfo('Minesweeper','You Won!')
                    self.master.destroy()
            except Exception as e:
                print("LSomething went wrong",e)
                self.board.print_board(True)

    def incRemaining(self):
    	self.mines_label["text"] = str( int(self.mines_label["text"]) + 1)

    def decRemaining(self):
    	self.mines_label["text"] = str( int(self.mines_label["text"]) - 1)

    def right_click(self,row, col):
	    if not self.isStarted:
		    self.isStarted=True
		    self.tick()
	    print('R',row,col)
	    try:
		    self.board.toggle_flag(row,col)
		    a = self.board.get_board_element( row, col)
		    if a == '#':
		        self.cells[row][col]["text"] = '     '
		        self.incRemaining()
		    elif a == 'P':
		        self.cells[row][col]["text"] = 'P'
		        self.decRemaining()
	    except Exception as e:
		    print("RSomething went wrong",e)
		    self.board.print_board(True)

    def update_all(self, show_mines=False):
	    for r in range(self.board.N):
		    for c in range(self.board.N):
			    a = self.board.get_board_element(r,c, show_mines)
			    if a == '#':
				    a = '     '
			    elif a == '0':
				    a = '     '
				    self.cells[r][c].config(bg='#AAFFAA')
			    elif a == '@':
				    a = '@'
			    elif a is not 'P':
				    self.cells[r][c]["fg"] = self.colors[int(a)]
			    self.cells[r][c]["text"] = a

	    self.master.update()


    def main(self,**kwargs):
        """
	    	Main loop of the program.
	    	kwargs are mostly used in test mode.
		It must be command as a list of commands!
        """
        while not self.isQuit and not self.lost and not self.board.won():
            try:
                self.doCommand(**kwargs)
                
            except (ValueError, IndexError) as e:
                if self.app_type == 'text' or self.app_type == 'test':
                    print("Invalid command")
                    if self.showWhy:
                            
                            print('\t',end='')
                            print(e)
            finally:
                if self.app_type == 'text':
                    self.board.print_board(False)
                if self.app_type == 'test':
                    self.board.print_board(False)
                    print('')
                    self.board.print_board(True)
                    print('')
        if self.lost:
            print("You lost!")
        elif self.board.won():
            print("You won!")
                    
    
    def getN_NumMines(self, **kwargs):
        """
		gets N and num_mines {from the user in text mode|from the kwargs in test mode}
	"""
        if self.app_type == 'text':
            N = int(input('Please input the size of board (e.g., 16): '))
            num_mines = int(input('Please input the number of mines (e.g., 15): '))
            return N, num_mines
        elif self.app_type == 'test':
            N = kwargs['N']
            num_mines = kwargs['num_mines']
            return N, num_mines
        elif self.app_type == 'gui':
            master = kwargs['master']
            master.withdraw()
            N = simpledialog.askinteger('Minesweeper','Enter Size of Map:',minvalue=1,maxvalue=25)#TODO: check min/max
            num_mines = simpledialog.askinteger('Minesweeper','Enter Number of Mines:',minvalue=1, maxvalue=N*N-1) #TODO: check min/max
            return N, num_mines
        
    def doCommand(self, **kwargs):
        """
		gets the command and calls functions to process it
	"""
        if self.app_type == 'text':
            command = input('command: ')
            self.processTextCommand(command)
        
        elif self.app_type == 'test':
            
            if self.idx < len(kwargs['command']):
                command = kwargs['command'][self.idx]
                print(command)
                self.idx += 1
                self.processTextCommand(command)
            else:
                self.isQuit = True
        
        elif self.app_type == 'gui':
            pass
        
    def processTextCommand(self,command):
        """
        	Processes a command.		
	"""
        f = command.split()
        has_error = True
        if len(f[0]) == 1:
            if f[0] in ['r','f','u','x']:                
                if f[0] == 'x' and len(f) == 1:     
                    has_error = False
                    self.isQuit = True
                elif len(f) == 3:
                    row = int(f[1])
                    col = int(f[2])
                    if f[0] == 'r':                        
                        x = self.board.reveal_cell(row,col)
                        has_error = False
                        if x == -1:
                            self.lost = True
                    elif f[0] == 'f':                        
                        self.board.put_flag(row,col)
                        has_error = False
                    elif f[0] == 'u':
                        self.board.remove_flag(row,col)
                        has_error = False
                        
        if has_error:
            error = ValueError('Invalid input')
            raise error


def main_text():
	try:
		app = App()
		app.main()
	except Exception as e:
		print("Something went wrong",e)


def main_gui():
	try:
		root = Tk()
		app = App('gui', False, master=root) # TODO: must make some small changes: 1- number of remaining mines,
		root.mainloop()
	except Exception as e:
		print("Something went wrong",e)

def test():
	app = App('test', True, N=8, num_mines=15)
	commands = ['f 0 0','u 0 0', 'u 1 1', 'r 0 0', 'r 7 7', 'r 8 8', 'w 1 1','r 4 5 3', 'r 5 4']
	app.main(command=commands)

if __name__ == "__main__":
	main_gui()
