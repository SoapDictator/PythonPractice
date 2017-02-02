import sys, random
import Tkinter as tk

class Application(object):
	valueResultiveDamage = 0
	optionAmmunition = ['1d4', '1d6', '1d8', '1d10']
	
	def __init__(self, root):
		root.title('Fallout Damage Calculator')
		frame = tk.Frame(root, width=280, height=140)
		frame.pack()
		
		self.valueDice = tk.StringVar()
		self.valueDice.set('Dice')
		self.droplistAmmo = tk.OptionMenu(root, self.valueDice, *self.optionAmmunition)
		self.entryID = tk.Entry(root)
		self.entryID.insert(tk.INSERT, '0')
		
		self.entryAC = tk.Entry(root)
		self.entryAC.insert(tk.INSERT, '0')
		
		self.entryDR = tk.Entry(root)
		self.entryDR.insert(tk.INSERT, '0')
		
		self.entryNS = tk.Entry(root)
		self.entryNS.insert(tk.INSERT, '1')
		
		self.buttonCalc = tk.Button(root, text = 'Calculate')
		self.buttonCalc.bind("<Button-1>", self.appCalculate)
		
		self.scrollbar = tk.Scrollbar(root)
		self.textRD = tk.Text(root, width = 20, height = 5, yscrollcommand=self.scrollbar.set)
		self.scrollbar.config(command = self.textRD.yview)
		
		self.allPack()

	def allPack(self):
		tk.Label(root, text = 'Initial Damage:').place(x = 10, y = 10, width = 105)
		self.entryID.place(x = 120, y = 10, width = 30)
		tk.Label(root, text = 'Ammunition:').place(x = 20, y = 35, width = 70)
		self.droplistAmmo.place(x = 95, y = 32, width = 60, height = 25)
		tk.Label(root, text = 'ArmorClass:').place(x = 10, y = 60, width = 105)
		self.entryAC.place(x = 120, y = 60, width = 30)
		tk.Label(root, text = 'Damage Resistance:').place(x = 10, y = 85, width = 105)
		self.entryDR.place(x = 120, y = 85, width = 30)
		tk.Label(root, text = 'Number of Shots:').place(x = 10, y = 110, width = 105)
		self.entryNS.place(x = 120, y = 110, width = 30)
		
		self.buttonCalc.place(x = 160, y = 10, width = 110)
		self.textRD.place(x = 160, y = 40, width = 90, height = 90)
		self.scrollbar.place(x = 252, y = 40, height = 90)
		
	def appCalculate(self, event):
		self.textRD.delete('1.0', tk.END)
		
		if self.entryNS.get() != '' and self.entryID.get() != '' and self.valueDice.get() != 'Dice' and self.entryAC.get() != '' and self.entryDR.get() != '':
			for i in range(0, int(self.entryNS.get())):
				valueHitChance = str(random.randint(0, 99))
				
				Ammo = self.valueDice.get()
				if Ammo == self.optionAmmunition[0]:
					valueAmmoFired = random.randint(0, 3)
				elif Ammo == self.optionAmmunition[1]:
					valueAmmoFired = random.randint(0, 5)
				elif Ammo == self.optionAmmunition[2]:
					valueAmmoFired = random.randint(0, 7)
				elif Ammo == self.optionAmmunition[3]:
					valueAmmoFired = random.randint(0, 9)
				
				valueInitialDamage = int(self.entryID.get()) + valueAmmoFired
				valueArmorClass = int(self.entryAC.get())
				valueDamageRes = float(self.entryDR.get()) / 100
				self.valueResultiveDamage = int((valueInitialDamage - valueArmorClass) - (valueInitialDamage - valueArmorClass)*valueDamageRes)
				
				returnString = valueHitChance+': '+str(self.valueResultiveDamage)+'\n'
				self.textRD.insert(tk.END, returnString)
		
root = tk.Tk()
app = Application(root)
root.mainloop()
#root.destroy()