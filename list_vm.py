from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl
import atexit

# Informations de connexion au vCenter
VCENTER_SERVER = 'votre_vcenter'
VCENTER_USER = 'votre_utilisateur'
VCENTER_PASSWORD = 'votre_mot_de_passe'
TARGET_FOLDER_NAME = 'nom_du_dossier_cible'

# Désactiver la vérification SSL (non sécurisé, mais nécessaire pour certains environnements)
context = ssl._create_unverified_context()

# Connexion au vCenter
si = SmartConnect(host=VCENTER_SERVER, user=VCENTER_USER, pwd=VCENTER_PASSWORD, sslContext=context)

# Assurer la déconnexion proprement
atexit.register(Disconnect, si)

def get_vm_folder(folder, target_folder_name):
    for child in folder.childEntity:
        if isinstance(child, vim.Folder):
            if child.name == target_folder_name:
                return child
            else:
                found_folder = get_vm_folder(child, target_folder_name)
                if found_folder:
                    return found_folder
    return None

def get_vms_from_folder(folder):
    vms = []
    for entity in folder.childEntity:
        if isinstance(entity, vim.VirtualMachine):
            vms.append(entity)
        elif isinstance(entity, vim.Folder):
            vms.extend(get_vms_from_folder(entity))
    return vms

def get_custom_attributes(vm):
    custom_attributes = {}
    for custom_field in vm.availableField:
        key = custom_field.key
        field_name = custom_field.name
        value = next((x.value for x in vm.value if x.key == key), None)
        custom_attributes[field_name] = value
    return custom_attributes

def main():
    content = si.RetrieveContent()
    root_folder = content.rootFolder

    # Récupération du dossier cible
    target_folder = get_vm_folder(root_folder, TARGET_FOLDER_NAME)
    if not target_folder:
        print(f"Le dossier '{TARGET_FOLDER_NAME}' n'a pas été trouvé.")
        return

    # Récupération des VMs du dossier cible
    vms = get_vms_from_folder(target_folder)
    
    # Créer un dictionnaire avec les custom attributes des VMs
    for vm in vms:
        custom_attributes = get_custom_attributes(vm)
        print(f"VM: {vm.name}, Custom Attributes: {custom_attributes}")

if __name__ == "__main__":
    main()
