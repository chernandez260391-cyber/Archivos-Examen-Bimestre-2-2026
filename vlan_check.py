try:
    vlan = int(input("Ingrese el número de VLAN: "))
    
    if 1 <= vlan <= 1005:
        print("La VLAN corresponde a un rango normal.")
    elif 1006 <= vlan <= 4094:
        print("La VLAN corresponde a un rango extendido.")
    else:
        print("El número no corresponde a una VLAN respectiva.")
except ValueError:
    print("Error: Por favor, ingrese un número entero válido.")
