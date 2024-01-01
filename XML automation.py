import re
import tkinter as tk
from tkinter import messagebox

patterns = [
    r"^[0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4}$",
    r"^[0-9A-Fa-f]{2}-[0-9A-Fa-f]{2}-[0-9A-Fa-f]{2}-[0-9A-Fa-f]{2}-[0-9A-Fa-f]{2}-[0-9A-Fa-f]{2}$",
    r"^[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}$",
    r"^[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}$",
]


def create_xml(vlan_name, vlan_number, switch_name, mac_addresses):
    xml_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<TipsContents xmlns="http://www.example.com">
\t<TipsHeader exportTime="Mon Nov 27 15:21:12 AST 2023" version="6.10"/>
\t<StaticHostLists>
\t\t<StaticHostList description="" name="SW {vlan_name} VLAN {vlan_number} {switch_name}" memberType="MACAddress" memberFormat="list">
\t\t\t<Members>
"""
    for member in mac_addresses:
        xml_content += f"\t\t\t\t{member}\n"

    xml_content += """\t\t\t</Members>
\t\t</StaticHostList>
\t</StaticHostLists>
</TipsContents>"""

    return xml_content


def validate_mac(mac):
    for pattern in patterns:
        if re.match(pattern, mac):
            return True
    return False


def create_file():
    vlan_name = entry_vlan_name.get()
    vlan_number = entry_vlan_number.get()
    switch_name = entry_switch_name.get()

    sanitized_vlan_name = "".join(c for c in vlan_name if c.isalnum())
    sanitized_vlan_number = "".join(c for c in vlan_number if c.isalnum())
    sanitized_switch_name = "".join(c for c in switch_name if c.isalnum())

    all_macs = entry_mac.get("1.0", tk.END).splitlines()
    valid_macs = []
    invalid_macs = []
    for mac in all_macs:
        if mac.strip() == "0":
            break
        if validate_mac(mac.strip()):
            input_str = mac.strip().replace(".", "").replace("-", "").replace(":", "")
            formatted_mac = "-".join(
                [input_str[i : i + 2] for i in range(0, len(input_str), 2)]
            )
            xml_element = f'<Member description="" address="{formatted_mac}"/>'
            valid_macs.append(xml_element)
        else:
            print(f"Ignored MAC: {mac.strip()}")
            invalid_macs.append(mac.strip())

    if invalid_macs and valid_macs:
        xml_data = create_xml(
            sanitized_vlan_name,
            sanitized_vlan_number,
            sanitized_switch_name,
            valid_macs,
        )
        file_name = f"SW {sanitized_vlan_name} VALN {sanitized_vlan_number} {sanitized_switch_name[:-1]}-{sanitized_switch_name[-1]}.xml"
        with open(file_name, "w") as file:
            file.write(xml_data)
        success_msg = (
            f"XML file was created but You have {len(invalid_macs)} invalid MAC(s):\n\n"
            + "\n".join(invalid_macs)
        )
        messagebox.showerror("Success", success_msg)
        print(f"File '{file_name}' created")
    elif not invalid_macs and valid_macs:
        xml_data = create_xml(
            sanitized_vlan_name,
            sanitized_vlan_number,
            sanitized_switch_name,
            valid_macs,
        )
        file_name = f"SW {sanitized_vlan_name} VALN {sanitized_vlan_number} {sanitized_switch_name[:-1]}-{sanitized_switch_name[-1]}.xml"
        with open(file_name, "w") as file:
            file.write(xml_data)
        success_msg = "XML file was created, all MACs are valid."
        messagebox.showinfo("Success", success_msg)
        print(f"File '{file_name}' created")
    else:
        confirm = messagebox.askyesno(
            "Confirmation", "All MACs are invalid. Do you want to create the file?"
        )
        if confirm:
            xml_data = create_xml(
                sanitized_vlan_name,
                sanitized_vlan_number,
                sanitized_switch_name,
                valid_macs,
            )
            file_name = f"SW {sanitized_vlan_name} VALN {sanitized_vlan_number} {sanitized_switch_name[:-1]}-{sanitized_switch_name[-1]}.xml"
            with open(file_name, "w") as file:
                file.write(xml_data)
            success_msg = "XML file was created, but all MACs are invalid."
            messagebox.showinfo("Success", success_msg)
            xml_data = create_xml(
                sanitized_vlan_name,
                sanitized_vlan_number,
                sanitized_switch_name,
                valid_macs,
            )
            print(f"File '{file_name}' created")

    print(f"File '{file_name}' created")


# GUI setup
root = tk.Tk()
root.title("XML Creator")

frame = tk.Frame(root)
frame.pack()

tk.Label(frame, text="VLAN NAME:").grid(row=0, column=0)
entry_vlan_name = tk.Entry(frame)
entry_vlan_name.grid(row=0, column=1)

tk.Label(frame, text="VLAN NUMBER:").grid(row=1, column=0)
entry_vlan_number = tk.Entry(frame)
entry_vlan_number.grid(row=1, column=1)

tk.Label(frame, text="SW NAME:").grid(row=2, column=0)
entry_switch_name = tk.Entry(frame)
entry_switch_name.grid(row=2, column=1)

tk.Label(frame, text="MAC addresses (Enter '0' on a new line to stop):").grid(
    row=3, column=0
)
entry_mac = tk.Text(frame, height=10, width=30)
entry_mac.grid(row=3, column=1)

btn_create = tk.Button(frame, text="Create XML File", command=create_file)
btn_create.grid(row=4, columnspan=2)

root.mainloop()
