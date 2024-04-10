use std::{collections::HashMap, error::Error, future::pending};
use zbus::{dbus_interface, ConnectionBuilder};

struct Greeter {
    count: u64,
}

#[dbus_interface(name = "org.zbus.MyGreeter1")]
impl Greeter {
    // Can be `async` as well.
    fn say_hello(&mut self, name: &str) -> String {
        self.count += 1;
        format!("Hello {}! I have been called {} times.", name, self.count)
    }

    #[dbus_interface(name = "Teardwon")]
    fn teardown(&mut self) {
        println!("tear it down");
    }

    #[dbus_interface(name = "Config")]
    fn config(&mut self) -> HashMap<String, String> {
        HashMap::new()
    }

    #[dbus_interface(name = "Run")]
    fn run(&mut self, match_id: &str, action_id: &str) {
        println!("match_id: {}, action_id: {}", match_id, action_id)
    }

    #[dbus_interface(name = "Match")]
    fn matches(&mut self, query: &str) -> Vec<String> {
        println!("get query: {}", query);
        vec!["a34".to_string(), "a35".to_string()]
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let greeter = Greeter { count: 0 };
    let _conn = ConnectionBuilder::session()?
        .name("org.zbus.MyGreeter")?
        .serve_at("/org/zbus/MyGreeter", greeter)?
        .build()
        .await?;

    // Do other things or go to wait forever
    pending::<()>().await;

    Ok(())
}

// busctl --user call org.zbus.MyGreeter /org/zbus/MyGreeter org.zbus.MyGreeter1 SayHello s "Maria"
