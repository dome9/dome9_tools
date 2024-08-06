import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import boto3
import subprocess
import pickle
import threading


class BaseConnectionParams:
    def __init__(self, aws_profile, default_db_port, local_port,
                 ssm_key_username, ssm_key_password, db_type, bastion_instance_name):
        self.aws_profile = aws_profile
        self.default_db_port = default_db_port
        self.local_port = local_port
        self.ssm_key_username = ssm_key_username
        self.ssm_key_password = ssm_key_password
        self.db_type = db_type
        self.bastion_instance_name = bastion_instance_name


class Ec2ConnectionParams(BaseConnectionParams):
    def __init__(self, aws_profile, default_db_port, local_port,
                 ssm_key_username, ssm_key_password, db_type, bastion_instance_name):
        # Call the base class constructor
        super().__init__(aws_profile, default_db_port, local_port,
                         ssm_key_username, ssm_key_password, db_type, bastion_instance_name)


class SessionConnectionParams(BaseConnectionParams):
    def __init__(self, aws_profile, default_db_port, local_port,
                 ssm_key_username, ssm_key_password,
                 ssm_key_db_endpoint, db_type, bastion_instance_name):
        # Call the base class constructor
        super().__init__(aws_profile, default_db_port, local_port,
                         ssm_key_username, ssm_key_password, db_type, bastion_instance_name)
        self.ssm_key_db_endpoint = ssm_key_db_endpoint


class AWSDBConnectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AWS DB Connector")
        self.config = None

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.stop_event = threading.Event()
        self.cmd_thread = None
        self.process = None

        self.InitUI(self.root)

    def on_close(self):
        self.stop_command()
        self.root.destroy()

    def stop_command(self):
        self.stop_event.set()
        if self.process:
            self.process.wait()
        if self.cmd_thread:
            self.cmd_thread.join()

    def InitUI(self, root):
        row_id = 0
        self.ec2_instance_id = tk.StringVar()

        self.load_button = tk.Button(root, text="Load Config", command=self.handle_load_object)
        self.load_button.grid(row=row_id, column=0, sticky=tk.EW)

        self.save_button = tk.Button(root, text="Save Config", command=self.handle_save_object)
        self.save_button.grid(row=row_id, column=1, sticky=tk.EW)

        row_id += 1
        self.message_label = tk.Label(root, text="")
        self.message_label.grid(row=row_id, column=0, sticky=tk.EW)
        row_id += 1

        # AWS Profile
        ttk.Label(root, text="AWS Profile Name:").grid(row=row_id, column=0, sticky=tk.W)
        self.aws_profile = tk.StringVar()
        ttk.Entry(root, textvariable=self.aws_profile).grid(row=row_id, column=1, sticky=tk.EW)
        row_id += 1
        # Default DB Port
        ttk.Label(root, text="DB Default Number:").grid(row=row_id, column=0, sticky=tk.W)
        self.default_db_port = tk.StringVar()
        ttk.Entry(root, textvariable=self.default_db_port).grid(row=row_id, column=1, sticky=tk.EW)
        row_id += 1
        # Local Port
        ttk.Label(root, text="Local Port Number:").grid(row=row_id, column=0, sticky=tk.W)
        self.local_port = tk.StringVar()
        ttk.Entry(root, textvariable=self.local_port).grid(row=row_id, column=1, sticky=tk.EW)
        row_id += 1
        # DB Type
        ttk.Label(root, text="DB Type:").grid(row=row_id, column=0, sticky=tk.W)
        self.db_type = tk.StringVar()
        self.db_type.set("EC2")
        self.ec2_radioButton = ttk.Radiobutton(root, text="EC2", variable=self.db_type, value="EC2",
                                               command=self.update_fields)
        self.ec2_radioButton.grid(row=row_id, column=1, sticky=tk.W)
        self.managed_radioButton = ttk.Radiobutton(root, text="Managed", variable=self.db_type, value="Managed",
                                                   command=self.update_fields)
        self.managed_radioButton.grid(row=row_id, column=2, sticky=tk.W)
        row_id += 1

        # SSM Key or Default for Username
        self.ssm_key_username_label = ttk.Label(root, text="SSM Key for Username or Default value:")
        self.ssm_key_username_label.grid(row=row_id, column=0, sticky=tk.W)
        self.ssm_key_username = tk.StringVar()
        self.ssm_key_username_entry = ttk.Entry(root, textvariable=self.ssm_key_username)
        self.ssm_key_username_entry.grid(row=row_id, column=1, sticky=tk.EW)
        row_id += 1
        # SSM Key or Default for Password
        self.ssm_key_password_label = ttk.Label(root, text="SSM Key for Password or Default value:")
        self.ssm_key_password_label.grid(row=row_id, column=0, sticky=tk.W)
        self.ssm_key_password = tk.StringVar()
        self.ssm_key_password_entry = ttk.Entry(root, textvariable=self.ssm_key_password)
        self.ssm_key_password_entry.grid(row=row_id, column=1, sticky=tk.EW)
        row_id += 1
        # Managed DB Endpoint URL
        self.ssm_key_db_endpoint_label = ttk.Label(root, text="SSM Key for DB Endpoint URL or Default (Managed DB only):")
        self.ssm_key_db_endpoint_label.grid(row=row_id, column=0, sticky=tk.W)
        self.ssm_key_db_endpoint = tk.StringVar()
        self.ssm_key_db_endpoint_entry = ttk.Entry(root, textvariable=self.ssm_key_db_endpoint)
        self.ssm_key_db_endpoint_entry.grid(row=row_id, column=1, sticky=tk.EW)
        row_id += 1
        # Bastion EC2 Instance Name
        self.bastion_instance_label = ttk.Label(root, text="Instance Name:")
        self.bastion_instance_label.grid(row=row_id, column=0, sticky=tk.W)
        self.bastion_instance_name = tk.StringVar()
        self.bastion_instance_entry = ttk.Entry(root, textvariable=self.bastion_instance_name)
        self.bastion_instance_entry.grid(row=row_id, column=1, sticky=tk.EW)
        row_id += 1

        # Connect Button
        ttk.Button(root, text="Connect", command=self.connect).grid(row=row_id, column=1, sticky=tk.EW)
        row_id += 1
        # Output Textbox for showing fetched SSM values
        self.output_text = tk.Text(root, height=10, width=50)
        self.output_text.grid(row=row_id, column=0, columnspan=3)
        row_id += 1
        # Initially update fields
        self.update_fields()

    def update_fields(self):
        db_type = self.db_type.get()
        if db_type == "EC2":
            self.ssm_key_username_label.grid()
            self.ssm_key_username_entry.grid()
            self.ssm_key_password_label.grid()
            self.ssm_key_password_entry.grid()
            self.bastion_instance_label.grid()
            self.bastion_instance_entry.grid()
            self.ssm_key_db_endpoint_label.grid_remove()
            self.ssm_key_db_endpoint_entry.grid_remove()
            self.bastion_instance_label.config(text="EC2 Instance Name:")
        elif db_type == "Managed":
            self.ssm_key_username_label.grid()
            self.ssm_key_username_entry.grid()
            self.ssm_key_password_label.grid()
            self.ssm_key_password_entry.grid()
            self.ssm_key_db_endpoint_label.grid()
            self.ssm_key_db_endpoint_entry.grid()
            self.bastion_instance_label.grid()
            self.bastion_instance_entry.grid()
            self.bastion_instance_label.config(text="Bastion EC2 Instance Name:")

    def handle_load_object(self):
        self.config = self.load_object()
        if self.config is not None:
            self.setParams()
            self.message_label.config(text="Object loaded successfully.")

    def handle_save_object(self):
        self.loadParams()
        if self.config is not None:
            self.save_object(self.config)
        else:
            self.message_label.config(text="No object to save.")

    def load_object(self):
        file_path = filedialog.askopenfilename(
            title="Select file",
            filetypes=(("Pickle files", "*.pkl"), ("All files", "*.*"))
        )
        if file_path:
            try:
                with open(file_path, 'rb') as file:
                    obj = pickle.load(file)
                    self.message_label.config(text=f"Object loaded from {file_path}")
                    return obj
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load object: {e}")
                return None
        return None

    def save_object(self, obj):
        file_path = filedialog.asksaveasfilename(
            title="Save file",
            defaultextension=".pkl",
            filetypes=(("Pickle files", "*.pkl"), ("All files", "*.*"))
        )
        if file_path:
            try:
                with open(file_path, 'wb') as file:
                    pickle.dump(obj, file)
                    self.message_label.config(text=f"Object saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save object: {e}")

    def get_ec2_instance_ids(self, instance_name):
        session = boto3.Session(profile_name=self.aws_profile.get())
        ec2 = session.client('ec2')
        response = ec2.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': [f'*{instance_name}*']}])

        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                instance_name = next(
                    (tag['Value'] for tag in instance['Tags'] if tag['Key'] == 'Name'), "No Name"
                )
                instances.append([instance_id, instance_name])

        return instances

    def retrieve_ssm_parameter(self, parameter_name, default_value):
        if not parameter_name:
            return default_value

        try:
            session = boto3.Session(profile_name=self.aws_profile.get())
            ssm = session.client('ssm')
            response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
            return response['Parameter']['Value']
        except ssm.exceptions.ParameterNotFound:
            return default_value
        except Exception as ex:
            raise Exception(f'Failed to fetch the ssm:{parameter_name}, ex={ex}')

    def get_caller_identity(self):
        session = boto3.Session(profile_name=self.aws_profile.get())
        sts = session.client('sts')
        return sts.get_caller_identity()

    def loadParams(self):
        aws_profile = self.aws_profile.get()
        db_port = self.default_db_port.get()
        local_port = self.local_port.get()
        db_type = self.db_type.get()
        ssm_key_username = self.ssm_key_username.get()
        ssm_key_password = self.ssm_key_password.get()
        ssm_key_db_endpoint = self.ssm_key_db_endpoint.get()
        bastion_instance_name = self.bastion_instance_name.get()

        if db_type == "EC2":
            self.config = Ec2ConnectionParams(
                aws_profile=aws_profile,
                default_db_port=db_port,
                local_port=local_port,
                ssm_key_username=ssm_key_username,
                ssm_key_password=ssm_key_password,
                db_type=db_type,
                bastion_instance_name=bastion_instance_name
            )

        else:
            self.config = SessionConnectionParams(
                aws_profile=aws_profile,
                default_db_port=db_port,
                local_port=local_port,
                ssm_key_username=ssm_key_username,
                ssm_key_password=ssm_key_password,
                ssm_key_db_endpoint=ssm_key_db_endpoint,
                bastion_instance_name=bastion_instance_name,
                db_type=db_type,
            )

    def setParams(self):
        self.aws_profile.set(self.config.aws_profile)
        self.default_db_port.set(self.config.default_db_port)
        self.local_port.set(self.config.local_port)
        self.db_type.set(self.config.db_type)
        self.ssm_key_username.set(self.config.ssm_key_username)
        self.ssm_key_password.set(self.config.ssm_key_password)
        self.bastion_instance_name.set(self.config.bastion_instance_name)

        if self.db_type.get() == "EC2":
            self.ec2_radioButton.config(state=tk.NORMAL)
        else:
            self.ssm_key_db_endpoint.set(self.config.ssm_key_db_endpoint)
            self.managed_radioButton.config(state=tk.NORMAL)
        self.update_fields()

    def connect(self):
        aws_profile = self.aws_profile.get()
        db_port = self.default_db_port.get()
        local_port = self.local_port.get()
        db_type = self.db_type.get()
        ssm_key_username = self.ssm_key_username.get()
        ssm_key_password = self.ssm_key_password.get()
        ssm_key_db_endpoint = self.ssm_key_db_endpoint.get()
        bastion_instance_name = self.bastion_instance_name.get()
        self.loadParams()

        try:
            # Fetch and display caller identity
            identity = self.get_caller_identity()
            identity_info = (
                f"Account: {identity['Account']}\n"
                f"UserID: {identity['UserId']}\n"
                f"ARN: {identity['Arn']}\n"
            )
            messagebox.showinfo("Caller Identity", identity_info)

            if not messagebox.askyesno("Confirm Connection", "Do you want to proceed with the connection?"):
                return

            # Configure AWS CLI with the selected profile
            subprocess.run(["aws", "configure", "set", "profile", aws_profile], check=True)

            # Handle multiple EC2 instances with the same name
            instances = self.get_ec2_instance_ids(bastion_instance_name)
            if len(instances) == 0:
                instance_selection = tk.Toplevel(self.root)
                instance_selection.title("Failed to find Instances")
                tk.Label(instance_selection, text="Failed to find Instances that match the name").pack()
                instance_selection.wait_window()
                return

            if len(instances) >= 1:
                instance_selection = tk.Toplevel(self.root)
                instance_selection.title("Select EC2 Instance")
                tk.Label(instance_selection, text="Multiple EC2 instances found. Please select one:").pack()

                self.ec2_instance_id = tk.StringVar()
                default_instance_id = instances[0][0]
                self.ec2_instance_id.set(default_instance_id)

                for idx, instance_data in enumerate(instances):
                    instance_id = instance_data[0]
                    instance_name = instance_data[1]
                    radioBtn = tk.Radiobutton(instance_selection, text=f'{instance_name}-{instance_id}',
                                   variable=self.ec2_instance_id, value=instance_id)
                    radioBtn.pack()

                tk.Button(instance_selection, text="Confirm", command=instance_selection.destroy).pack()
                instance_selection.wait_window()

            print(f'selected; {self.ec2_instance_id.get()}')

            # Retrieve SSM parameters if specified
            username = self.retrieve_ssm_parameter(ssm_key_username, ssm_key_username)
            password = self.retrieve_ssm_parameter(ssm_key_password, ssm_key_password)

            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Username: {username}\n")
            self.output_text.insert(tk.END, f"Password: {password}\n")
            if db_type == "Managed":
                db_endpoint = self.retrieve_ssm_parameter(ssm_key_db_endpoint,
                                                          ssm_key_db_endpoint) if db_type == "Managed" else None
                self.output_text.insert(tk.END, f"DB Endpoint: {db_endpoint}\n")

            if db_type == "EC2":
                # Start Port Forwarding for EC2 instance
                command = self.GetEc2ConnectCommand(aws_profile, db_port, local_port)
            elif db_type == "Managed":
                # Start Port Forwarding for Managed DB
                command = self.GetAwsSessionCommand(aws_profile, db_endpoint, db_port, local_port)

            self.run_command(command)
            self.output_text.insert(tk.END, f"the command:\n{' '.join(command)}.\n")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to establish connection: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to establish connection: {e}")

    def GetAwsSessionCommand(self, aws_profile, db_endpoint, db_port, local_port):
        command = [
            "aws", "ssm", "start-session",
            "--target", self.ec2_instance_id.get(),
            "--document-name", "AWS-StartPortForwardingSessionToRemoteHost",
            "--parameters", f"host='{db_endpoint}',portNumber='{db_port}',localPortNumber='{local_port}'",
            "--profile", aws_profile
        ]
        return command

    def GetEc2ConnectCommand(self, aws_profile, db_port, local_port):
        command = [
            "aws", "ssm", "start-session",
            "--target", self.ec2_instance_id.get(),
            "--document-name", "AWS-StartPortForwardingSession",
            "--parameters", f"portNumber='{db_port}',localPortNumber='{local_port}'",
            "--profile", aws_profile
        ]
        return command

    def run_command(self, command):
        if self.cmd_thread is None or not self.cmd_thread.is_alive():
            self.stop_event.clear()
            self.cmd_thread = threading.Thread(target=self.execute_command, args=(command,))
            self.cmd_thread.start()

    def execute_command(self, command):
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        while not self.stop_event.is_set():
            output = self.process.stdout.readline()
            if output:
                self.append_text(output)

        self.process.stdout.close()
        self.process.terminate()  # Terminate the process if stop_event is set
        self.process.wait()  # Wait for the process to terminate

    def append_text(self, text):
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)  # Scroll to the end


if __name__ == "__main__":
    root = tk.Tk()
    app = AWSDBConnectorApp(root)
    root.mainloop()
